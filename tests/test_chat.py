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


def test_chat_returns_answer_from_injected_service() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        chat_service=FakeChatService(),
    )

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json() == {"answer": "Echo: hello"}


def test_chat_returns_503_when_azure_chat_is_not_configured() -> None:
    app = create_app(settings=Settings(_env_file=None))

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "message": "Azure OpenAI chat is not configured.",
            "missing_settings": [
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_API_VERSION",
                "AZURE_OPENAI_CHAT_DEPLOYMENT",
            ],
        }
    }


def test_chat_rejects_empty_message() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        chat_service=FakeChatService(),
    )

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422


def test_chat_returns_502_when_chat_service_fails() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        chat_service=FailingChatService(),
    )

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 502
    assert response.json() == {
        "detail": {
            "message": "Azure OpenAI deployment was not found.",
        }
    }
