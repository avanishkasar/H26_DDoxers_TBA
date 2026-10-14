from typing import Annotated, cast

from fastapi import Depends, Request

from app.llm import OllamaClient


def get_llm(request: Request) -> OllamaClient:
    return cast(OllamaClient, request.app.state.llm)


LLMDep = Annotated[OllamaClient, Depends(get_llm)]
