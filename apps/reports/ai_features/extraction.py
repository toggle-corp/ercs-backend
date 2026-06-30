import base64
import json
import logging
from dataclasses import dataclass, field

import fitz
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI

from apps.reports.ai_features.llms import OllamaHandler
from apps.reports.ai_features.prompts import get_doc_summary_prompt
from apps.reports.models import DocumentExtraction, DocumentExtractionStatus, Report

logger = logging.getLogger(__name__)


@dataclass
class BaseExtraction:
    report: Report

    llm_handler: OllamaHandler = field(init=False)
    llm_chat_model: ChatOllama | ChatOpenAI = field(init=False)
    llm_embedding_model: OllamaEmbeddings = field(init=False)

    def __post_init__(self):
        try:
            self.llm_handler = OllamaHandler()
            self.llm_chat_model = self.llm_handler.load_chat_model()
            self.llm_embedding_model = self.llm_handler.load_embedding_model()
        except Exception as e:
            raise e

    def handle_meta_info(self):
        """Extract meta information of the report."""
        title = self.report.title
        description = self.report.description
        if title and title.strip():
            DocumentExtraction.objects.create(
                report=self.report,
                status=DocumentExtractionStatus.SUCCESS,
                text=title,
                page_number=None,
                chunk_type=DocumentExtraction.ExtractionType.TITLE,
                embedding=self.llm_embedding_model.embed_query(title),
            )
        if description and description.strip():
            DocumentExtraction.objects.create(
                report=self.report,
                status=DocumentExtractionStatus.SUCCESS,
                text=description,
                page_number=None,
                chunk_type=DocumentExtraction.ExtractionType.DESCRIPTION,
                embedding=self.llm_embedding_model.embed_query(description),
            )


@dataclass
class PdfExtraction(BaseExtraction):
    data: bytes

    def img_to_base64(self, data: fitz.Pixmap) -> str:
        img_bytes = data.tobytes("png")
        return base64.b64encode(img_bytes).decode("utf-8")

    def pdf_to_images(self, zoom: float = 2.0):
        page_summaries = []
        doc = fitz.open(stream=self.data, filetype="pdf")

        # Get the title and description
        self.handle_meta_info()

        for page_idx in range(len(doc)):
            page = doc[page_idx]

            pic = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            img_b64 = self.img_to_base64(data=pic)

            message = self.llm_handler.construct_extraction_message(img_b64=img_b64)

            response = self.llm_chat_model.invoke([message])
            if not isinstance(response.content, str):
                continue
            result = json.loads(response.content)

            if "summary" in result and result["summary"]:
                page_summaries.append(result["summary"])

            if "extracted_text" in result and result["extracted_text"]:
                DocumentExtraction.objects.create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["extracted_text"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.EXTRACTED_CONTENT,
                    embedding=self.llm_embedding_model.embed_query(result["extracted_text"]),
                )
            if "key_findings" in result and result["key_findings"]:
                DocumentExtraction.objects.create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["key_findings"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.KEYWORDS,
                    embedding=self.llm_embedding_model.embed_query(result["key_findings"]),
                )
            if "tables" in result and result["tables"]:
                DocumentExtraction.objects.create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["tables"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.TABLE,
                    embedding=self.llm_embedding_model.embed_query(json.dumps(result["tables"])),
                )
            if "charts" in result and result["charts"]:
                DocumentExtraction.objects.create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["charts"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.CHART,
                    embedding=self.llm_embedding_model.embed_query(json.dumps(result["charts"])),
                )

        doc_summary_prompt = get_doc_summary_prompt(page_summaries=page_summaries)
        doc_summary = self.llm_chat_model.invoke(doc_summary_prompt)
        if not isinstance(doc_summary.content, str):
            return
        doc_summary_json = json.loads(doc_summary.content)
        if doc_summary_json and "doc_summary" in doc_summary_json:
            DocumentExtraction.objects.create(
                report=self.report,
                status=DocumentExtractionStatus.SUCCESS,
                text=doc_summary_json["doc_summary"],
                page_number=None,
                chunk_type=DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY,
                embedding=self.llm_embedding_model.embed_query(doc_summary_json["doc_summary"]),
            )
        else:
            logger.warning("The key doc_summary is missing in the output")


@dataclass
class HeaderExtraction(BaseExtraction):
    """Get the basic meta information extraction."""
