from typing import Protocol

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory

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


class ChatService(Protocol):
    async def complete(self, message: str) -> str:
        """Return an assistant answer for a user message."""


class SemanticKernelChatService:
    def __init__(self, settings: Settings) -> None:
        missing_settings = settings.missing_chat_settings()
        if missing_settings:
            raise ChatConfigurationError(missing_settings)

        self._kernel = Kernel()
        self._chat_completion = AzureChatCompletion(
            deployment_name=settings.azure_openai_chat_deployment,
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
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
        result = await self._chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=self._kernel,
        )
        return str(result)
