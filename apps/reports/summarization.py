
from dataclasses import dataclass
from pathlib import Path
import fitz
from .prompts import PAGE_PROMPT
from langchain_openai import ChatOpenAI 
import base64
#from langchain_community.llms.ollama import Ollama
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage
import json
import typing

from .models import DocumentExtraction, DocumentExtractionStatus, Report


LLM_MODEL_NAME = "qwen2.5vl:7b"
LLM_OLLAMA_BASE_URL = "https://ollama.k8s.local.togglecorp.com"
LLM_EMBEDDING_MODEL = "nomic-embed-text:v1.5"

@dataclass
class OpenAIHandler:
    """LLM inference using OpenAI"""
    temperature: float = 0.2

    def __init__(self):
        try:
            self.llm_model = ChatOpenAI(model=LLM_MODEL_NAME, temperature=self.temperature)
        except Exception as e:
            raise Exception(f"OpenAI LLM model is not successfully loaded. {str(e)}")

@dataclass
class OllamaHandler:
    """LLM Handler using Ollama for RAG"""
    temperature: float = 0.1

    def load_chat_model(self):
        try:
            llm_model = ChatOllama(
                model=LLM_MODEL_NAME, base_url=LLM_OLLAMA_BASE_URL, temperature=self.temperature, format="json" 
            )
            return llm_model
        except Exception as e:
            raise Exception(f"Ollama LLM model is not successfully loaded. {str(e)}")

    def load_embedding_model(self):
        try:
            llm_embedding_model = OllamaEmbeddings(
                model=LLM_EMBEDDING_MODEL, base_url=LLM_OLLAMA_BASE_URL,
            )
            return llm_embedding_model
        except Exception as e:
            raise Exception(f"Ollama LLM model is not successfully loaded. {str(e)}")


@dataclass
class PdfExtraction:
    report: typing.Any
    source_file_path: typing.Any 
    
    def __post_init__(self):
        try:
            llm_handler = OllamaHandler()
            self.llm_chat_model = llm_handler.load_chat_model()
            self.llm_embedding_model = llm_handler.load_embedding_model()
        except Exception as e:
            raise e

    def img_to_base64(self, data: fitz.Pixmap):
        img_bytes = data.tobytes("png")
        return base64.b64encode(img_bytes).decode("utf-8")
 
    async def pdf_to_images(self, zoom: float=2.0):
        #doc = fitz.open(self.source_file_path)
        doc = fitz.open(stream=self.source_file_path, filetype="pdf")

        for page_idx in range(len(doc)):
            page = doc[page_idx]

            pic = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            img_b64 = self.img_to_base64(data=pic)
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": PAGE_PROMPT,
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{img_b64}",
                    },
                ],
            )

            response = self.llm_chat_model.invoke([message])
            print(f"Page num: {page_idx}")
            #print(response)
            result = json.loads(response.content)

            print(f"result: {result}")

            if "summary" in result and result["summary"]:
                await DocumentExtraction.objects.aupdate_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["summary"],
                    page_number=None,
                    chunk_type=DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY,
                    embedding=self.llm_embedding_model.embed_query(result["summary"])
                )
            if "extracted_text" in result and result["extracted_text"]:
                await DocumentExtraction.objects.aupdate_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["extracted_text"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.EXTRACTED_CONTENT,
                    embedding=self.llm_embedding_model.embed_query(result["extracted_text"])
                )
            if "key_findings" in result and result["key_findings"]: 
                await DocumentExtraction.objects.aupdate_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["key_findings"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.KEYWORDS,
                    embedding=self.llm_embedding_model.embed_query(result["key_findings"])
                )
            if "tables" in result and result["tables"]:
                await DocumentExtraction.objects.aupdate_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["tables"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.TABLE,
                    embedding=self.llm_embedding_model.embed_query(json.dumps(result["tables"]))
                )
            if "charts" in result and result["charts"]:
                await DocumentExtraction.objects.aupdate_or_create(
                    report=self.report,
                    status=DocumentExtractionStatus.SUCCESS,
                    text=result["charts"],
                    page_number=page_idx + 1,
                    chunk_type=DocumentExtraction.ExtractionType.CHART,
                    embedding=self.llm_embedding_model.embed_query(json.dumps(result["charts"]))
                )
