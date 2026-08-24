import re
import typing
from collections import defaultdict
from dataclasses import dataclass, field

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models.functions import Greatest
from langchain_core.embeddings import Embeddings
from pgvector.django import CosineDistance

from apps.reports.ai_features.llms import get_embedding_llm_handler
from apps.reports.models import DocumentExtraction, DocumentExtractionStatus, Report

# ts_rank normalization: divide rank by (rank + 1), bounding it to [0, 1) so it is
# comparable to the [0, 1] cosine similarity score used for semantic search.
KEYWORD_RANK_NORMALIZATION = 32

# Per-part trust levels: how reliable a chunk type is as a relevance signal, not how
# much text it tends to contain. Parts written or curated by a person (title,
# description, summaries) are trusted more than raw machine-extracted text, which
# carries boilerplate, headers/footers, and passing mentions indistinguishable from
# genuine "aboutness". These are reasoned starting points, not measurements against
# this specific corpus - revisit once a real query/relevance eval set exists.
WEIGHTS: dict[int, float] = {
    DocumentExtraction.ExtractionType.TITLE: 1.00,
    DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY: 0.8,
    DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY_SHORT: 0.98,
    DocumentExtraction.ExtractionType.PAGE_SUMMARY: 0.80,
    DocumentExtraction.ExtractionType.DESCRIPTION: 0.80,
    DocumentExtraction.ExtractionType.KEYWORDS: 0.70,
    DocumentExtraction.ExtractionType.TABLE: 0.45,
    DocumentExtraction.ExtractionType.EXTRACTED_CONTENT: 0.45,
    DocumentExtraction.ExtractionType.CHART: 0.45,
}
DEFAULT_CHUNK_WEIGHT = 0.5

# Decayed additive bonus for supporting chunks beyond the best match, so a report
# with more relevant evidence can only ever score higher, never lower.
SUPPORTING_CHUNK_DECAY = 0.5
SUPPORTING_CHUNK_WEIGHT = 0.15
MAX_SUPPORTING_CHUNKS = 3


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


class ChunkScore(typing.TypedDict):
    score: float
    chunk_type: str


@dataclass
class SearchReports:
    """Search and rank reports based on user query using hybrid (semantic + keyword) search."""

    query: str
    # Spam guard: if even the best-matching report can't reach this score, there is
    # no real match - return nothing rather than noise. Not an absolute pass bar for
    # every result (see `relative_cutoff`).
    score_threshold: float = 0.5
    # Keep only results within this fraction of the top result's score, so ranking
    # doesn't silently recouple to a fixed absolute number tied to the current
    # embedding model/weights.
    relative_cutoff: float = 0.7
    semantic_weight: float = 0.65
    keyword_weight: float = 0.35
    max_chunks_per_report: int = 3
    llm_embedding_model: Embeddings = field(init=False)

    def __post_init__(self):
        self.llm_embedding_model = get_embedding_llm_handler().load_embedding_model()

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
                # 1 - CosineDistance can go slightly negative (opposite-direction vectors);
                # clamp so it stays a valid [0, 1] similarity score.
                score=Greatest(
                    1 - CosineDistance("embedding", query_vector),
                    0.0,
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
        """Combine semantic and keyword scores into a single hybrid score per chunk.

        Caps how many chunks any single report can contribute so a large, comprehensive
        document can't occupy the whole candidate pool and starve smaller reports out.
        """
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

        ranked_chunks = sorted(chunks, key=lambda chunk: chunk.score, reverse=True)  # type: ignore[attr-defined]

        capped_chunks = []
        chunks_per_report: defaultdict[int, int] = defaultdict(int)
        for chunk in ranked_chunks:
            if chunks_per_report[chunk.report.pk] >= self.max_chunks_per_report:
                continue
            chunks_per_report[chunk.report.pk] += 1
            capped_chunks.append(chunk)

        return capped_chunks[:k_top]

    def group_by_reports(self) -> tuple[defaultdict[int, list[ChunkScore]], dict[int, Report]]:
        """Group chunk scores by report id, alongside the already-loaded Report objects."""
        reports_with_scores = defaultdict(list)
        reports_by_id: dict[int, Report] = {}
        results = self.get_scores()

        for result in results:
            reports_with_scores[result.report.pk].append(
                {
                    "score": result.score,  # type: ignore[attr-defined]
                    "chunk_type": result.chunk_type,
                },
            )
            reports_by_id[result.report.pk] = result.report

        return reports_with_scores, reports_by_id

    def calculate_weighted_score(self, chunks: list[ChunkScore]) -> float:
        """Calculate a report's score from its chunks: best match plus a decayed bonus for support.

        Monotonic in evidence - adding a relevant chunk can only raise the score, never
        lower it, unlike an average which is dragged down by weaker supporting matches.
        """
        weighted_scores = [
            chunk["score"] * WEIGHTS.get(DocumentExtraction.ExtractionType(chunk["chunk_type"]), DEFAULT_CHUNK_WEIGHT)
            for chunk in chunks
        ]

        top_scores = sorted(weighted_scores, reverse=True)
        supporting_bonus = sum(
            SUPPORTING_CHUNK_WEIGHT * (SUPPORTING_CHUNK_DECAY**i) * score
            for i, score in enumerate(top_scores[1 : MAX_SUPPORTING_CHUNKS + 1], start=1)
        )
        return top_scores[0] + supporting_bonus

    def rank_reports(self, top_k: int = 10) -> list[Report]:
        """Rank the reports."""
        reports_with_scores, reports_by_id = self.group_by_reports()
        normalized_query = _normalize_text(self.query)

        ranked_docs = []
        for report_id, chunks in reports_with_scores.items():
            score = self.calculate_weighted_score(chunks)
            if _normalize_text(reports_by_id[report_id].title) == normalized_query:
                # Known-item lookup: the user typed the document's exact name. That's
                # close to dispositive - guarantee it ranks first regardless of weighting.
                score = float("inf")
            ranked_docs.append((report_id, score))

        ranked_docs.sort(key=lambda x: x[1], reverse=True)

        # Exact title matches always make the cut; the relative cutoff/floor guard
        # below only governs the rest, so a known-item hit doesn't suppress other
        # genuinely relevant results.
        exact_matches = [doc for doc in ranked_docs if doc[1] == float("inf")]
        scored_docs = [doc for doc in ranked_docs if doc[1] != float("inf")]

        strong_docs = exact_matches
        if scored_docs and scored_docs[0][1] >= self.score_threshold:
            cutoff = self.relative_cutoff * scored_docs[0][1]
            strong_docs += [doc for doc in scored_docs if doc[1] >= cutoff]
        return [reports_by_id[report_id] for report_id, _ in strong_docs[:top_k]]
