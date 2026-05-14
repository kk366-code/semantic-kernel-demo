import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from semantic_kernel_api.config import Settings, get_settings
from semantic_kernel_api.schemas import ChatRequest, ChatResponse, HealthResponse
from semantic_kernel_api.services.chat import (
    ChatConfigurationError,
    ChatService,
    ChatServiceError,
    SemanticKernelChatService,
)

PACKAGE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")
logger = logging.getLogger(__name__)


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
    app.mount(
        "/static",
        StaticFiles(directory=PACKAGE_DIR / "static"),
        name="static",
    )
    app.state.settings = resolved_settings
    app.state.chat_service = chat_service

    if chat_service is None and resolved_settings.is_chat_configured():
        app.state.chat_service = SemanticKernelChatService(resolved_settings)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "chat_configured": request.app.state.chat_service is not None,
                "missing_settings": request.app.state.settings.missing_chat_settings(),
            },
        )

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
        except ChatServiceError as error:
            logger.warning("Azure OpenAI chat API request failed: %s", error.log_detail)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "message": error.message,
                },
            ) from error

        return ChatResponse(answer=answer)

    @app.post("/chat/ui", response_class=HTMLResponse)
    async def chat_ui(request: Request) -> HTMLResponse:
        form = await request.form()
        message = str(form.get("message", "")).strip()
        if not message:
            return templates.TemplateResponse(
                request,
                "partials/chat_result.html",
                {
                    "error": "メッセージを入力してください。",
                    "message": message,
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        service = request.app.state.chat_service
        if service is None:
            missing_settings = request.app.state.settings.missing_chat_settings()
            return templates.TemplateResponse(
                request,
                "partials/chat_result.html",
                {
                    "error": "Azure OpenAI chat is not configured.",
                    "missing_settings": missing_settings,
                    "message": message,
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            answer = await service.complete(message)
        except ChatConfigurationError as error:
            return templates.TemplateResponse(
                request,
                "partials/chat_result.html",
                {
                    "error": "Azure OpenAI chat is not configured.",
                    "missing_settings": error.missing_settings,
                    "message": message,
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ChatServiceError as error:
            logger.warning("Azure OpenAI chat UI request failed: %s", error.log_detail)
            return templates.TemplateResponse(
                request,
                "partials/chat_result.html",
                {
                    "error": error.message,
                    "message": message,
                },
                status_code=status.HTTP_502_BAD_GATEWAY,
            )

        return templates.TemplateResponse(
            request,
            "partials/chat_result.html",
            {
                "answer": answer,
                "message": message,
            },
        )

    return app


app = create_app()
