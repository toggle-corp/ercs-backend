import json
from dataclasses import dataclass

import httpx
from django.conf import settings
from langchain_core.embeddings import Embeddings
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter
from sentence_transformers import SentenceTransformer

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

    def generate_structured(self, chat_model, messages, schema: dict, context_window: int | None = None) -> dict:
        """Invoke the chat model and return its response parsed against `schema`."""
        raise NotImplementedError


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

    def generate_structured(self, chat_model, messages, schema: dict, context_window: int | None = None) -> dict:
        options = {"num_ctx": context_window} if context_window else None
        response = chat_model.invoke(messages, format=schema, **({"options": options} if options else {}))
        if not isinstance(response.content, str):
            raise TypeError("Response content is not a string")
        return json.loads(response.content)


@dataclass
class OpenRouterHandler(LLMHandler):
    """LLM Handler using OpenRouter (chat completions only, no embeddings support)."""

    model_name: str = "test"
    max_tokens: int = 16384
    # Reasoning is opt-in: many OpenRouter models (e.g. gemma-3-12b-it) don't
    # support it, and the API may reject or ignore the field if sent regardless.
    reasoning: dict | None = None

    def load_chat_model(self):
        try:
            reasoning_kwargs = {"reasoning": self.reasoning} if self.reasoning else {}
            return ChatOpenRouter(
                model=settings.LLM_MODEL_NAME or self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                api_key=settings.OPENROUTER_API_KEY,
                **reasoning_kwargs,
            )
        except Exception as e:
            raise Exception(f"OpenRouter LLM model is not successfully loaded. {str(e)}") from e

    def generate_structured(self, chat_model, messages, schema: dict, context_window: int | None = None) -> dict:
        # context_window has no OpenRouter equivalent to Ollama's num_ctx override;
        # the model's own context window applies.
        return chat_model.with_structured_output(schema, method="json_schema").invoke(messages)


class SentenceTransformerEmbeddings(Embeddings):
    """Embeddings backed directly by a local sentence-transformers model."""

    def __init__(self, model_name: str):
        self._model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()


@dataclass
class SentenceTransformerHandler(LLMHandler):
    """Embeddings-only handler using a local sentence-transformers model."""

    def load_embedding_model(self):
        try:
            return SentenceTransformerEmbeddings(model_name=settings.SENTENCE_TRANSFORMER_MODEL_NAME)
        except Exception as e:
            raise Exception(f"Sentence-transformers embedding model is not successfully loaded. {str(e)}") from e


def get_chat_llm_handler() -> LLMHandler:
    """Return the handler to use for chat completions, per LLM_USE_OPENROUTER."""
    if settings.LLM_USE_OPENROUTER:
        return OpenRouterHandler()
    return OllamaHandler()


def get_embedding_llm_handler() -> LLMHandler:
    """Return the handler to use for embeddings, per LLM_USE_SENTENCE_TRANSFORMERS."""
    if settings.LLM_USE_SENTENCE_TRANSFORMERS:
        return SentenceTransformerHandler()
    return OllamaHandler()
