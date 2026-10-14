"""Async client for a local Ollama server (Gemma 4 or any other open-weight model)."""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.config import Settings
from app.schemas import ChatMessage

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the model server is unreachable or returns an error."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class OllamaClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self._default_model = settings.ollama_model
        self._client = httpx.AsyncClient(
            base_url=str(settings.ollama_base_url),
            timeout=httpx.Timeout(
                settings.llm_read_timeout_s, connect=settings.llm_connect_timeout_s
            ),
            transport=transport,
        )
        # Local inference is GPU/CPU bound; queue excess requests instead of thrashing the box.
        self._semaphore = asyncio.Semaphore(settings.llm_max_concurrency)

    @property
    def default_model(self) -> str:
        return self._default_model

    async def aclose(self) -> None:
        await self._client.aclose()

    async def list_models(self) -> list[str]:
        try:
            resp = await self._client.get("/api/tags", timeout=5.0)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMError(f"Model server unreachable: {exc}", 503) from exc
        return [m["name"] for m in resp.json().get("models", [])]

    def _payload(
        self, messages: list[ChatMessage], model: str | None, temperature: float, stream: bool
    ) -> dict[str, Any]:
        return {
            "model": model or self._default_model,
            "messages": [m.model_dump() for m in messages],
            "stream": stream,
            "options": {"temperature": temperature},
        }

    async def chat(
        self, messages: list[ChatMessage], model: str | None = None, temperature: float = 0.7
    ) -> ChatMessage:
        payload = self._payload(messages, model, temperature, stream=False)
        async with self._semaphore:
            try:
                resp = await self._client.post("/api/chat", json=payload)
            except httpx.TimeoutException as exc:
                raise LLMError("Model server timed out", 504) from exc
            except httpx.HTTPError as exc:
                raise LLMError(f"Model server unreachable: {exc}", 503) from exc
        if resp.is_error:
            raise LLMError(f"Model server error {resp.status_code}: {resp.text[:500]}")
        return ChatMessage.model_validate(resp.json()["message"])

    async def chat_stream(
        self, messages: list[ChatMessage], model: str | None = None, temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Yield content deltas. Ollama streams newline-delimited JSON objects."""
        payload = self._payload(messages, model, temperature, stream=True)
        async with self._semaphore:
            try:
                async with self._client.stream("POST", "/api/chat", json=payload) as resp:
                    if resp.is_error:
                        body = (await resp.aread()).decode(errors="replace")
                        raise LLMError(f"Model server error {resp.status_code}: {body[:500]}")
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line)
                        if err := chunk.get("error"):
                            raise LLMError(str(err))
                        if delta := chunk.get("message", {}).get("content"):
                            yield delta
                        if chunk.get("done"):
                            return
            except httpx.TimeoutException as exc:
                raise LLMError("Model server timed out", 504) from exc
            except httpx.HTTPError as exc:
                raise LLMError(f"Model server unreachable: {exc}", 503) from exc
