import typing
from collections import defaultdict
from dataclasses import dataclass, field

from django.contrib.postgres.search import SearchQuery, SearchRank
from langchain_ollama import OllamaEmbeddings
from pgvector.django import CosineDistance

from apps.reports.ai_features.llms import OllamaHandler
from apps.reports.models import DocumentExtraction, DocumentExtractionStatus, Report

# ts_rank normalization: divide rank by (rank + 1), bounding it to [0, 1) so it is
# comparable to the [0, 1] cosine similarity score used for semantic search.
KEYWORD_RANK_NORMALIZATION = 32


class ChunkScore(typing.TypedDict):
    score: float
    chunk_type: str


@dataclass
class SearchReports:
    """Search and rank reports based on user query using hybrid (semantic + keyword) search."""

    query: str
    score_threshold: float = 0.4
    semantic_weight: float = 0.6
    keyword_weight: float = 0.4
    llm_embedding_model: OllamaEmbeddings = field(init=False)
    weights: dict[int, float] = field(init=False)

    def __post_init__(self):
        llm_handler = OllamaHandler()
        self.llm_embedding_model = llm_handler.load_embedding_model()

        self.weights: dict[int, float] = {
            DocumentExtraction.ExtractionType.EXTRACTED_CONTENT: 0.9,
            DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY: 0.7,
            DocumentExtraction.ExtractionType.PAGE_SUMMARY: 0.7,
            DocumentExtraction.ExtractionType.KEYWORDS: 0.9,
            DocumentExtraction.ExtractionType.TABLE: 0.3,
            DocumentExtraction.ExtractionType.CHART: 0.3,
            DocumentExtraction.ExtractionType.TITLE: 0.2,
            DocumentExtraction.ExtractionType.DESCRIPTION: 0.2,
        }

    def generate_query_embedding(self) -> list[float]:
        """Return the vector of the query."""
        return self.llm_embedding_model.embed_query(self.query)

    def get_semantic_scores(self, k_top: int = 100) -> dict[int, float]:
        """Return chunk id -> cosine similarity score for the top matching chunks."""
        query_vector = self.generate_query_embedding()
        results = (
            DocumentExtraction.objects.filter(status=DocumentExtractionStatus.SUCCESS)
            .filter(embedding__isnull=False)
            .annotate(
                score=1
                - CosineDistance(
                    "embedding",
                    query_vector,
                ),
            )
            .order_by("-score")[:k_top]
        )
        return {result.pk: result.score for result in results}  # type: ignore[attr-defined]

    def get_keyword_scores(self, k_top: int = 100) -> dict[int, float]:
        """Return chunk id -> normalized full-text-search rank for the top matching chunks."""
        search_query = SearchQuery(self.query)
        results = (
            DocumentExtraction.objects.filter(status=DocumentExtractionStatus.SUCCESS)
            .annotate(score=SearchRank("text", search_query, normalization=KEYWORD_RANK_NORMALIZATION))
            .filter(score__gt=0)
            .order_by("-score")[:k_top]
        )
        return {result.pk: result.score for result in results}  # type: ignore[attr-defined]

    def get_scores(self, k_top: int = 100) -> list[DocumentExtraction]:
        """Combine semantic and keyword scores into a single hybrid score per chunk."""
        semantic_scores = self.get_semantic_scores(k_top)
        keyword_scores = self.get_keyword_scores(k_top)

        chunks = DocumentExtraction.objects.filter(
            pk__in=set(semantic_scores) | set(keyword_scores),
        ).select_related("report")

        for chunk in chunks:
            chunk.score = (  # type: ignore[attr-defined]
                semantic_scores.get(chunk.pk, 0.0) * self.semantic_weight
                + keyword_scores.get(chunk.pk, 0.0) * self.keyword_weight
            )

        return sorted(chunks, key=lambda chunk: chunk.score, reverse=True)[:k_top]  # type: ignore[attr-defined]

    def group_by_reports(self) -> defaultdict[int, list[ChunkScore]]:
        """Group the reports by report id."""
        reports_with_scores = defaultdict(list)
        results = self.get_scores()

        for result in results:
            reports_with_scores[result.report.pk].append(
                {
                    "score": result.score,  # type: ignore[attr-defined]
                    "chunk_type": result.chunk_type,
                },
            )
        return reports_with_scores

    def calculate_weighted_score(self, chunks: list[ChunkScore]) -> float:
        """Calculate the weighted score of different chunks of the report."""
        weighted_scores = []
        for chunk in chunks:
            weighted_scores.append(chunk["score"] * self.weights[DocumentExtraction.ExtractionType(chunk["chunk_type"])])

        # Give extra weight to the max score and low weight to the average score value
        top_scores = sorted(weighted_scores, reverse=True)  # sort scores in desc order
        return max(top_scores) * 0.6 + (sum(top_scores) / len(top_scores)) * 0.4

    def rank_reports(self, top_k: int = 10) -> list[Report]:
        """Rank the reports."""
        reports_with_scores = self.group_by_reports()
        ranked_docs = []

        for report_id, chunks in reports_with_scores.items():
            score = self.calculate_weighted_score(chunks)
            if score >= self.score_threshold:
                ranked_docs.append((report_id, score))

        ranked_docs.sort(key=lambda x: x[1], reverse=True)

        # Retrieve the top k reports
        doc_ids = [doc_id for doc_id, _ in ranked_docs[:top_k]]
        reports_by_id = {
            d.id: d
            for d in Report.objects.filter(
                id__in=doc_ids,
            )
        }
        # Return ordered reports
        return [reports_by_id[rep_id] for rep_id, _ in ranked_docs[:top_k]]
