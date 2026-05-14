from typing import Annotated, Protocol

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function

from semantic_kernel_api.config import Settings
from semantic_kernel_api.services.chat import ChatConfigurationError

PROJECT_GUIDE_AGENT_NAME = "ProjectGuideAgent"

PROJECT_GUIDE_AGENT_INSTRUCTIONS = """
You are ProjectGuideAgent, a concise Japanese guide for this FastAPI and Semantic Kernel
sample application.

Help users understand the current project scope, available API endpoints, development commands,
quality checks, and small next demos they can try. Use your project guide tools when the user asks
about project APIs, commands, or architecture. Be clear when a feature is not implemented yet or
when configuration is unknown. Do not claim that RAG, Azure CLI tools, or multi-agent orchestration
are implemented in this v1 agent.
""".strip()


class AgentService(Protocol):
    async def complete(self, message: str) -> str:
        """Return an agent answer for a user message."""


class ProjectGuidePlugin:
    """Read-only project guide tools for the Semantic Kernel agent."""

    @kernel_function(description="Return the public API endpoints currently available.")
    def get_public_apis(self) -> Annotated[str, "A concise list of public API endpoints."]:
        return """
GET / - Minimal HTMX page for trying chat and agent responses.
GET /health - Returns application health status.
POST /chat - Sends a single message to the basic Semantic Kernel chat service.
POST /chat/ui - Returns an HTML fragment for the chat form.
POST /agent - Sends a single message to ProjectGuideAgent.
POST /agent/ui - Returns an HTML fragment for the agent form.
""".strip()

    @kernel_function(description="Return development and quality check commands.")
    def get_development_commands(
        self,
    ) -> Annotated[str, "Development and quality check commands for this project."]:
        return """
uv sync
uv run fastapi dev src/semantic_kernel_api/main.py
uv run uvicorn semantic_kernel_api.main:app --app-dir src --reload
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run pre-commit run --all-files
""".strip()

    @kernel_function(description="Return the current architecture summary.")
    def get_architecture_summary(
        self,
    ) -> Annotated[str, "A concise summary of the current application architecture."]:
        return """
The app is a FastAPI sample with an app factory, thin route handlers, Pydantic request and
response models, Jinja2 + HTMX templates, a basic Semantic Kernel chat service, and this
ProjectGuideAgent. Azure OpenAI provides the chat completion model. Postgres + pgvector RAG,
Azure CLI tools, persistent conversation history, and multi-agent orchestration are planned for
later milestones.
""".strip()


class SemanticKernelAgentService:
    def __init__(self, settings: Settings) -> None:
        missing_settings = settings.missing_chat_settings()
        if missing_settings:
            raise ChatConfigurationError(missing_settings)

        chat_completion = AzureChatCompletion(
            deployment_name=settings.azure_openai_chat_deployment,
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version or None,
        )
        self._agent = ChatCompletionAgent(
            service=chat_completion,
            name=PROJECT_GUIDE_AGENT_NAME,
            instructions=PROJECT_GUIDE_AGENT_INSTRUCTIONS,
            plugins=[ProjectGuidePlugin()],
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )

    async def complete(self, message: str) -> str:
        response = await self._agent.get_response(messages=message)
        return str(response)
