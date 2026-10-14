import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.deps import LLMDep
from app.llm import LLMError
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest, llm: LLMDep) -> ChatResponse:
    message = await llm.chat(body.messages, body.model, body.temperature)
    return ChatResponse(model=body.model or llm.default_model, message=message)


@router.post("/stream")
async def chat_stream(body: ChatRequest, llm: LLMDep) -> StreamingResponse:
    """Server-Sent Events: `data: {"delta": "..."}` frames, then `data: [DONE]`."""

    async def events() -> AsyncIterator[str]:
        try:
            async for delta in llm.chat_stream(body.messages, body.model, body.temperature):
                yield f"data: {json.dumps({'delta': delta})}\n\n"
        except LLMError as exc:
            # Headers are already sent, so surface errors in-band.
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
