from fastapi.testclient import TestClient

from semantic_kernel_api.config import Settings
from semantic_kernel_api.main import create_app
from semantic_kernel_api.services.chat import ChatServiceError


class FakeChatService:
    async def complete(self, message: str) -> str:
        return f"Echo: {message}"


class FailingChatService:
    async def complete(self, message: str) -> str:
        raise ChatServiceError("Azure OpenAI deployment was not found.")


def test_index_renders_chat_page() -> None:
    app = create_app(settings=Settings(_env_file=None))

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Azure OpenAI Chat" in response.text
    assert "Azure OpenAI settings are incomplete." in response.text


def test_chat_ui_returns_answer_fragment() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        chat_service=FakeChatService(),
    )

    with TestClient(app) as client:
        response = client.post("/chat/ui", data={"message": "hello"})

    assert response.status_code == 200
    assert "Echo: hello" in response.text


def test_chat_ui_returns_missing_settings_fragment() -> None:
    app = create_app(settings=Settings(_env_file=None))

    with TestClient(app) as client:
        response = client.post("/chat/ui", data={"message": "hello"})

    assert response.status_code == 503
    assert "Azure OpenAI chat is not configured." in response.text
    assert "AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_BASE_URL" in response.text
    assert "AZURE_OPENAI_API_VERSION" in response.text


def test_chat_ui_returns_service_error_fragment() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        chat_service=FailingChatService(),
    )

    with TestClient(app) as client:
        response = client.post("/chat/ui", data={"message": "hello"})

    assert response.status_code == 502
    assert "Azure OpenAI deployment was not found." in response.text
