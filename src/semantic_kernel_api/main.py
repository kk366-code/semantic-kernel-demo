from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status

from semantic_kernel_api.config import Settings, get_settings
from semantic_kernel_api.schemas import ChatRequest, ChatResponse, HealthResponse
from semantic_kernel_api.services.chat import (
    ChatConfigurationError,
    ChatService,
    SemanticKernelChatService,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.ready = True
    yield


def create_app(
    *,
    settings: Settings | None = None,
    chat_service: ChatService | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title="Semantic Kernel API",
        summary="Minimal FastAPI API prepared for Semantic Kernel, Azure OpenAI, and RAG.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.chat_service = chat_service

    if chat_service is None and resolved_settings.is_chat_configured():
        app.state.chat_service = SemanticKernelChatService(resolved_settings)

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/chat", response_model=ChatResponse)
    async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
        service = request.app.state.chat_service
        if service is None:
            missing_settings = request.app.state.settings.missing_chat_settings()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Azure OpenAI chat is not configured.",
                    "missing_settings": missing_settings,
                },
            )

        try:
            answer = await service.complete(payload.message)
        except ChatConfigurationError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Azure OpenAI chat is not configured.",
                    "missing_settings": error.missing_settings,
                },
            ) from error

        return ChatResponse(answer=answer)

    return app


app = create_app()
