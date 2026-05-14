from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.ready = True
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Semantic Kernel API",
        summary="Minimal FastAPI API prepared for Semantic Kernel, Azure OpenAI, and RAG.",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
