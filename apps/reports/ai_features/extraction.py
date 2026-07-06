import base64
import io
import json
import logging
import time
from dataclasses import dataclass, field

import fitz
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI
from PIL import Image

from apps.reports.ai_features.llms import OllamaHandler
from apps.reports.ai_features.prompts import DOC_SUMMARY_SCHEMA, PAGE_SCHEMA, get_doc_summary_prompt
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

    # Qwen2.5-VL uses a native dynamic-resolution vision encoder, so the number of
    # vision tokens (and Ollama's memory/compute use) scales with input pixel count.
    # Cap the longest side so oversized source pages can't blow up memory regardless
    # of the render zoom.
    MAX_IMAGE_DIMENSION = 1024

    # Retries for a single page's LLM extraction call, covering transient network/
    # timeout errors as well as malformed or truncated JSON in the model's response.
    MAX_PAGE_ATTEMPTS = 3
    PAGE_RETRY_DELAY_SECONDS = 3

    def img_to_base64(self, data: fitz.Pixmap) -> str:
        img_bytes = data.tobytes("png")

        image = Image.open(io.BytesIO(img_bytes))
        if max(image.size) > self.MAX_IMAGE_DIMENSION:
            scale = self.MAX_IMAGE_DIMENSION / max(image.size)
            new_size = (round(image.width * scale), round(image.height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()

        return base64.b64encode(img_bytes).decode("utf-8")

    def extract_page(self, page_idx: int, img_b64: str) -> dict | None:
        """Run the LLM extraction call for a single page, retrying on failure."""
        message = self.llm_handler.construct_extraction_message(img_b64=img_b64)

        for attempt in range(1, self.MAX_PAGE_ATTEMPTS + 1):
            try:
                response = self.llm_chat_model.invoke([message], format=PAGE_SCHEMA)
                if not isinstance(response.content, str):
                    raise TypeError("Response content is not a string")  # noqa: TRY301
                return json.loads(response.content)
            except Exception:
                logger.warning(
                    "Page %s extraction attempt %s/%s failed",
                    page_idx + 1,
                    attempt,
                    self.MAX_PAGE_ATTEMPTS,
                    exc_info=True,
                )
                if attempt < self.MAX_PAGE_ATTEMPTS:
                    time.sleep(self.PAGE_RETRY_DELAY_SECONDS)

        logger.error("Page %s extraction failed after %s attempts", page_idx + 1, self.MAX_PAGE_ATTEMPTS)
        return None

    def pdf_to_images(self, zoom: float = 1.1):
        page_summaries = []
        doc = fitz.open(stream=self.data, filetype="pdf")

        # Get the title and description
        self.handle_meta_info()
        # Doc Summary In Pending State
        doc_summary_obj = DocumentExtraction.objects.create(
            report=self.report,
            status=DocumentExtractionStatus.PENDING,
            text="",
            page_number=None,
            chunk_type=DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY,
            embedding=None,
        )

        for page_idx in range(len(doc)):
            logger.info("Processing Page %s", page_idx + 1)
            page = doc[page_idx]

            pic = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            img_b64 = self.img_to_base64(data=pic)

            result = self.extract_page(page_idx=page_idx, img_b64=img_b64)
            if result is None:
                DocumentExtraction.objects.create(
                    report=self.report,
                    status=DocumentExtractionStatus.FAILURE,
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.EXTRACTED_CONTENT,
                )
                continue

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
        # This prompt concatenates every page's summary, so its input size scales with
        # page count. Override back up to the original context window rather than the
        # smaller per-page default, since a lower window here can silently truncate
        # earlier page summaries out of the final document summary.
        doc_summary = self.llm_chat_model.invoke(
            doc_summary_prompt,
            format=DOC_SUMMARY_SCHEMA,
            options={"num_ctx": 8192},
        )
        if not isinstance(doc_summary.content, str):
            return
        try:
            doc_summary_json = json.loads(doc_summary.content)
            DocumentExtraction.objects.filter(pk=doc_summary_obj.pk).update(
                status=DocumentExtractionStatus.SUCCESS,
                text=doc_summary_json["doc_summary"],
                embedding=self.llm_embedding_model.embed_query(doc_summary_json["doc_summary"]),
            )
        except (ValueError, KeyError):
            logger.warning("Either key doc_summary is missing or malformed json in the output.")
            DocumentExtraction.objects.filter(pk=doc_summary_obj.pk).update(
                status=DocumentExtractionStatus.FAILURE,
            )


@dataclass
class HeaderExtraction(BaseExtraction):
    """Get the basic meta information extraction."""
