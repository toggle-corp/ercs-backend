from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI

from apps.reports.ai_features.prompts import PAGE_PROMPT

LLM_MODEL_NAME = "qwen2.5vl:7b"
LLM_OLLAMA_BASE_URL = "https://ollama.k8s.local.togglecorp.com"
LLM_EMBEDDING_MODEL = "nomic-embed-text:v1.5"


@dataclass
class LLMHandler:
    temperature: float = 0.2

    def construct_extraction_message(self, img_b64: bytes) -> HumanMessage:
        return HumanMessage(
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


@dataclass
class OpenAIHandler(LLMHandler):
    """LLM inference using OpenAI."""

    def __init__(self):
        try:
            self.llm_model = ChatOpenAI(model=LLM_MODEL_NAME, temperature=self.temperature)
        except Exception as e:
            raise Exception(f"OpenAI LLM model is not successfully loaded. {str(e)}") from e


@dataclass
class OllamaHandler(LLMHandler):
    """LLM Handler using Ollama."""

    def load_chat_model(self):
        try:
            return ChatOllama(
                model=LLM_MODEL_NAME,
                base_url=LLM_OLLAMA_BASE_URL,
                temperature=self.temperature,
                format="json",
            )
        except Exception as e:
            raise Exception(f"Ollama LLM model is not successfully loaded. {str(e)}") from e

    def load_embedding_model(self):
        try:
            return OllamaEmbeddings(
                model=LLM_EMBEDDING_MODEL,
                base_url=LLM_OLLAMA_BASE_URL,
            )
        except Exception as e:
            raise Exception(f"Ollama LLM model is not successfully loaded. {str(e)}") from e
