import json
from collections.abc import AsyncIterator

import httpx
import pytest

from app.config import Settings
from app.llm import OllamaClient
from app.main import create_app


def ollama_mock(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/api/tags":
        return httpx.Response(200, json={"models": [{"name": "gemma4:latest"}]})
    if request.url.path == "/api/chat":
        body = json.loads(request.content)
        if body["stream"]:
            lines = [
                {"message": {"role": "assistant", "content": "Hel"}, "done": False},
                {"message": {"role": "assistant", "content": "lo"}, "done": True},
            ]
            return httpx.Response(200, text="\n".join(json.dumps(x) for x in lines))
        return httpx.Response(200, json={"message": {"role": "assistant", "content": "Hello"}})
    return httpx.Response(404)


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    settings = Settings(ollama_model="gemma4")
    llm = OllamaClient(settings, transport=httpx.MockTransport(ollama_mock))
    app = create_app(settings, llm)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


async def test_health(client: httpx.AsyncClient) -> None:
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {
        "status": "ok",
        "llm_reachable": True,
        "model": "gemma4",
        "model_available": True,
    }


async def test_chat(client: httpx.AsyncClient) -> None:
    resp = await client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert resp.status_code == 200
    assert resp.json()["message"]["content"] == "Hello"


async def test_chat_stream(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/chat/stream", json={"messages": [{"role": "user", "content": "hi"}]}
    )
    frames = [ln[6:] for ln in resp.text.splitlines() if ln.startswith("data: ")]
    assert frames[-1] == "[DONE]"
    assert "".join(json.loads(f)["delta"] for f in frames[:-1]) == "Hello"


async def test_chat_rejects_empty_messages(client: httpx.AsyncClient) -> None:
    resp = await client.post("/api/chat", json={"messages": []})
    assert resp.status_code == 422


async def test_unreachable_model_server() -> None:
    def down(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    settings = Settings()
    app = create_app(settings, OllamaClient(settings, transport=httpx.MockTransport(down)))
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as c:
            health = await c.get("/api/health")
            assert health.json()["llm_reachable"] is False
            chat = await c.post("/api/chat", json={"messages": [{"role": "user", "content": "x"}]})
            assert chat.status_code == 503
