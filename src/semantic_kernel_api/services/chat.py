from typing import Protocol

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.exceptions.service_exceptions import ServiceResponseException

from semantic_kernel_api.config import Settings

DEFAULT_SYSTEM_PROMPT = (
    "You are a concise assistant for a FastAPI and Semantic Kernel sample application. "
    "Answer clearly and mention uncertainty when configuration or context is missing."
)


class ChatConfigurationError(RuntimeError):
    def __init__(self, missing_settings: list[str]) -> None:
        self.missing_settings = missing_settings
        joined = ", ".join(missing_settings)
        super().__init__(f"Missing Azure OpenAI settings: {joined}")


class ChatServiceError(RuntimeError):
    def __init__(self, message: str, *, log_detail: str | None = None) -> None:
        self.message = message
        self.log_detail = log_detail or message
        super().__init__(message)


class ChatService(Protocol):
    async def complete(self, message: str) -> str:
        """Return an assistant answer for a user message."""


class SemanticKernelChatService:
    def __init__(self, settings: Settings) -> None:
        missing_settings = settings.missing_chat_settings()
        if missing_settings:
            raise ChatConfigurationError(missing_settings)

        self._kernel = Kernel()
        endpoint = settings.azure_openai_endpoint or None
        base_url = settings.azure_openai_base_url or None
        self._chat_completion = AzureChatCompletion(
            deployment_name=settings.azure_openai_chat_deployment,
            api_key=settings.azure_openai_api_key,
            endpoint=endpoint,
            base_url=base_url,
            api_version=settings.azure_openai_api_version,
        )
        self._kernel.add_service(self._chat_completion)

    async def complete(self, message: str) -> str:
        history = ChatHistory()
        history.add_system_message(DEFAULT_SYSTEM_PROMPT)
        history.add_user_message(message)

        execution_settings = AzureChatPromptExecutionSettings(
            temperature=0.2,
            max_tokens=800,
        )
        try:
            result = await self._chat_completion.get_chat_message_content(
                chat_history=history,
                settings=execution_settings,
                kernel=self._kernel,
            )
        except ServiceResponseException as error:
            raise ChatServiceError(
                _format_service_error(error),
                log_detail=_format_service_log_detail(error),
            ) from error

        return str(result)


def _format_service_error(error: ServiceResponseException) -> str:
    error_text = str(error)
    if "DeploymentNotFound" in error_text:
        return (
            "Azure OpenAI deployment was not found. "
            "Check AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_ENDPOINT, and wait a few minutes "
            "if the deployment was just created."
        )
    return "Azure OpenAI chat request failed. Check the server logs and Azure OpenAI settings."


def _format_service_log_detail(error: ServiceResponseException) -> str:
    error_text = str(error)
    if "DeploymentNotFound" in error_text:
        return (
            "Azure OpenAI request failed: DeploymentNotFound. "
            "Check AZURE_OPENAI_CHAT_DEPLOYMENT and AZURE_OPENAI_ENDPOINT. "
            f"Raw error: {error_text}"
        )
    return f"Azure OpenAI request failed. Raw error: {error_text}"
