# FastAPI Semantic Kernel MVP

FastAPI, Semantic Kernel, Azure OpenAI, and Postgres + pgvector を段階的に組み合わせるためのサンプルアプリケーションです。最初のマイルストーンでは、開発ルール、Python tooling、最小 REST API、テストを用意しています。

## Current Scope

- FastAPI app factory
- `GET /health`
- pytest API test
- Ruff format/lint configuration
- `uv` based dependency management
- Future Azure OpenAI and Postgres/pgvector environment placeholders

RAG、Semantic Kernel 実接続、AIエージェント機能、DB migration は次のマイルストーンで追加します。

## Requirements

- Python 3.12 or newer
- `uv`

## Setup

```bash
uv sync
cp .env.example .env
```

## Run

```bash
uv run fastapi dev src/semantic_kernel_api/main.py
```

Alternative:

```bash
uv run uvicorn semantic_kernel_api.main:app --app-dir src --reload
```

Then open:

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Quality Checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

## Initial Architecture

```text
src/semantic_kernel_api/
├── __init__.py
└── main.py          # FastAPI app factory and health endpoint

tests/
└── test_health.py   # HTTP-level health endpoint test
```

Near-term additions:

- settings module with `pydantic-settings`
- Semantic Kernel service factory for Azure OpenAI
- Postgres + pgvector persistence
- document ingestion and RAG chat endpoints

## Environment Variables

See `.env.example` for the planned configuration names. Real secrets should only be stored in local `.env` files or deployment secret stores.

