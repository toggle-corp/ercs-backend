from dataclasses import dataclass

import httpx
from django.conf import settings
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI

from apps.reports.ai_features.prompts import PAGE_PROMPT


@dataclass
class LLMHandler:
    temperature: float = 0.0

    def construct_extraction_message(self, img_b64: str) -> HumanMessage:
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
            self.llm_model = ChatOpenAI(model=settings.LLM_MODEL_NAME, temperature=self.temperature)
        except Exception as e:
            raise Exception(f"OpenAI LLM model is not successfully loaded. {str(e)}") from e


@dataclass
class OllamaHandler(LLMHandler):
    """LLM Handler using Ollama."""

    def load_chat_model(self):
        try:
            return ChatOllama(
                model=settings.LLM_MODEL_NAME,
                base_url=settings.LLM_OLLAMA_BASE_URL,
                temperature=self.temperature,
                # Sized for a single page (prompt + one page's vision tokens + JSON output).
                # The multi-page document summary call needs a larger window and overrides
                # this via `options={"num_ctx": ...}` at call time.
                num_ctx=4096,
                client_kwargs={
                    "timeout": httpx.Timeout(
                        connect=30.0,
                        read=600.0,  # Allow up to 10 minutes for generation
                        write=300.0,
                        pool=30.0,
                    ),
                },
            )
        except Exception as e:
            raise Exception(f"Ollama LLM model is not successfully loaded. {str(e)}") from e

    def load_embedding_model(self):
        try:
            return OllamaEmbeddings(
                model=settings.LLM_EMBEDDING_MODEL,
                base_url=settings.LLM_OLLAMA_BASE_URL,
            )
        except Exception as e:
            raise Exception(f"Ollama LLM model is not successfully loaded. {str(e)}") from e
