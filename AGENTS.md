# FastAPI Semantic Kernel MVP - Agent Guide

## Project Purpose
- Build a minimal REST API sample with FastAPI, Semantic Kernel, Azure OpenAI, and a future Postgres + pgvector RAG layer.
- Treat `Semantic Kernel` as the canonical spelling in docs and code comments.
- Keep the first milestone small: project tooling, `/health`, tests, and documentation.

## Package Management
- Use `uv` for all Python project management.
- Do not write `pip install` instructions for normal development.
- Add dependencies with `uv add <package>`.
- Sync dependencies with `uv sync`.
- Run commands through `uv run ...`.
- Commit `uv.lock`.

## Python Style
- Target Python `>=3.12`; local Python 3.13 is supported.
- Prefer modern type syntax: use `X | None`, `list[T]`, and `dict[K, V]`.
- Use `TYPE_CHECKING` for forward references when imports are only needed by type checkers.
- Keep route handlers thin and move application behavior into service modules as the project grows.

## Formatting and Linting
- Use Ruff for both formatting and linting.
- Do not add Black, Flake8, or isort.
- Quality gates:
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run pytest`
- Ruff configuration belongs in `pyproject.toml`.

## FastAPI Rules
- Use an app factory named `create_app`.
- Use FastAPI lifespan for shared resources such as database pools, Semantic Kernel services, and Azure OpenAI clients.
- Keep the initial `/health` endpoint simple and dependency-light.
- Prefer explicit Pydantic models for request and response bodies once non-trivial APIs are added.

## AI and RAG Rules
- The MVP provider is Azure OpenAI through Semantic Kernel.
- Do not add a multi-provider LLM abstraction until there is a real second provider requirement.
- Store secret values only in local `.env` files or deployment secrets; never commit them.
- Keep `.env.example` limited to variable names and safe placeholder values.
- Use Postgres + pgvector as the first RAG storage target in later milestones.
- Do not require local embedding models or `fastembed` for this project.

## Documentation Rules
- Update `README.md` when setup, commands, architecture, environment variables, or public API behavior changes.
- When introducing a new SDK or framework API for the first time, check official documentation before implementing.
- Explain meaningful new files or structural changes briefly in the final response.

## Session Handoff Rules
- If the conversation context becomes heavy, slow, or likely to lose important details, suggest starting a new chat.
- When suggesting a new chat, provide a concise handoff note that includes:
  - current repository path and GitHub URL
  - current branch and latest commit
  - completed work and verification results
  - next recommended task
  - any important project rules from this file that the next session should preserve
- Keep handoff notes short enough to paste into a new chat without bringing unnecessary history.

## Command and Git Rules
- Before running commands with notable side effects, explain the purpose and side effects in Japanese.
- Never revert user changes unless explicitly asked.
- Keep commits focused and use English commit titles, for example `chore: bootstrap FastAPI Semantic Kernel project`.
- PR creation is not mandatory for the initial local sample unless the user requests it.
