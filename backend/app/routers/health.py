from fastapi import APIRouter

from app.deps import LLMDep
from app.llm import LLMError
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(llm: LLMDep) -> HealthResponse:
    try:
        models = await llm.list_models()
    except LLMError:
        return HealthResponse(
            status="ok", llm_reachable=False, model=llm.default_model, model_available=False
        )
    # Ollama reports "gemma4:latest" for a bare "gemma4" pull.
    wanted = llm.default_model
    available = wanted in models or f"{wanted}:latest" in models
    return HealthResponse(status="ok", llm_reachable=True, model=wanted, model_available=available)
