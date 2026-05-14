# FastAPI Semantic Kernel MVP

FastAPI, Semantic Kernel, Azure OpenAI, and Postgres + pgvector を段階的に組み合わせるためのサンプルアプリケーションです。最初のマイルストーンでは、開発ルール、Python tooling、最小 REST API、テストを用意しています。

## Current Scope

- FastAPI app factory
- `GET /health`
- `POST /chat` API shape for Semantic Kernel + Azure OpenAI
- Azure OpenAI settings loader
- pytest API test
- Ruff format/lint configuration
- `uv` based dependency management
- Future Postgres/pgvector environment placeholders

Azure OpenAI の環境変数を設定すると、`/chat` は Semantic Kernel 経由で chat deployment を呼び出します。RAG、AIエージェント機能、DB migration は次のマイルストーンで追加します。

## Requirements

- Python 3.12 or newer
- `uv`

## Setup

```bash
uv sync
cp .env.example .env
uv run pre-commit install
```

This project uses Gitleaks as a pre-commit secret scanner. Install the `gitleaks` CLI before installing the hook:

```bash
brew install gitleaks
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

## Chat API

Azure OpenAI の設定がある場合:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "content-type: application/json" \
  -d '{"message":"Semantic Kernelとは何ですか？"}'
```

Response:

```json
{
  "answer": "..."
}
```

Azure OpenAI の設定が足りない場合は `503 Service Unavailable` を返し、不足している環境変数名を `missing_settings` に含めます。

## Quality Checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run pre-commit run --all-files
```

## Initial Architecture

```text
src/semantic_kernel_api/
├── __init__.py
├── config.py        # pydantic-settings based app configuration
├── main.py          # FastAPI app factory and API routes
├── schemas.py       # request/response models
└── services/
    └── chat.py      # Semantic Kernel chat service boundary

tests/
├── test_chat.py     # chat endpoint tests with a fake service
└── test_health.py   # HTTP-level health endpoint test
```

Near-term additions:

- Postgres + pgvector persistence
- document ingestion and RAG chat endpoints

## Environment Variables

See `.env.example` for the planned configuration names. Real secrets should only be stored in local `.env` files or deployment secret stores.

Minimum variables for `/chat`:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION` optional, but recommended when your Azure resource requires a specific API version
