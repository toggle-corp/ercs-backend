import base64
import json
import typing
from dataclasses import dataclass

import fitz

from apps.reports.ai_features.llms import OllamaHandler
from apps.reports.ai_features.prompts import get_doc_summary_prompt
from apps.reports.models import DocumentExtraction, DocumentExtractionStatus, Report


@dataclass
class PdfExtraction:
    report: Report
    source_file_path: typing.Any

    def __post_init__(self):
        try:
            self.llm_handler = OllamaHandler()
            self.llm_chat_model = self.llm_handler.load_chat_model()
            self.llm_embedding_model = self.llm_handler.load_embedding_model()
        except Exception as e:
            raise e

    def img_to_base64(self, data: fitz.Pixmap):
        img_bytes = data.tobytes("png")
        return base64.b64encode(img_bytes).decode("utf-8")

    def pdf_to_images(self, zoom: float = 2.0):
        # doc = fitz.open(self.source_file_path)
        page_summaries = []
        doc = fitz.open(stream=self.source_file_path, filetype="pdf")

        for page_idx in range(len(doc)):
            page = doc[page_idx]

            pic = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            img_b64 = self.img_to_base64(data=pic)

            message = self.llm_handler.construct_extraction_message(img_b64=img_b64)

            response = self.llm_chat_model.invoke([message])
            result = json.loads(response.content)

            if "summary" in result and result["summary"]:
                page_summaries.append(result["summary"])

            if "extracted_text" in result and result["extracted_text"]:
                DocumentExtraction.objects.update_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["extracted_text"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.EXTRACTED_CONTENT,
                    embedding=self.llm_embedding_model.embed_query(result["extracted_text"]),
                )
            if "key_findings" in result and result["key_findings"]:
                DocumentExtraction.objects.update_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["key_findings"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.KEYWORDS,
                    embedding=self.llm_embedding_model.embed_query(result["key_findings"]),
                )
            if "tables" in result and result["tables"]:
                DocumentExtraction.objects.update_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["tables"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.TABLE,
                    embedding=self.llm_embedding_model.embed_query(json.dumps(result["tables"])),
                )
            if "charts" in result and result["charts"]:
                DocumentExtraction.objects.update_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["charts"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.CHART,
                    embedding=self.llm_embedding_model.embed_query(json.dumps(result["charts"])),
                )

        doc_summary_prompt = get_doc_summary_prompt(page_summaries=page_summaries)
        doc_summary = self.llm_chat_model.invoke(doc_summary_prompt)
        doc_summary_json = json.loads(doc_summary.content)

        if doc_summary_json:
            DocumentExtraction.objects.update_or_create(
                report=self.report,
                status=DocumentExtractionStatus.SUCCESS,
                text=doc_summary_json["Executive Summary"],
                page_number=None,
                chunk_type=DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY,
                embedding=self.llm_embedding_model.embed_query(doc_summary_json["Executive Summary"]),
            )
