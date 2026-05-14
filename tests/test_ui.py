from fastapi.testclient import TestClient

from semantic_kernel_api.config import Settings
from semantic_kernel_api.main import create_app


class FakeChatService:
    async def complete(self, message: str) -> str:
        return f"Echo: {message}"


class FakeAgentService:
    async def complete(self, message: str) -> str:
        return f"Agent: {message}"


def test_index_renders_chat_page() -> None:
    app = create_app(settings=Settings(_env_file=None))

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Azure OpenAI Chat & Agent" in response.text
    assert "Chat:" in response.text
    assert "Agent:" in response.text


def test_chat_ui_returns_answer_fragment() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        chat_service=FakeChatService(),
    )

    with TestClient(app) as client:
        response = client.post("/chat/ui", data={"message": "hello"})

    assert response.status_code == 200
    assert "Echo: hello" in response.text


def test_agent_ui_returns_answer_fragment() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        agent_service=FakeAgentService(),
    )

    with TestClient(app) as client:
        response = client.post("/agent/ui", data={"message": "hello"})

    assert response.status_code == 200
    assert "ProjectGuideAgent" in response.text
    assert "Agent: hello" in response.text


def test_chat_ui_returns_missing_settings_fragment() -> None:
    app = create_app(settings=Settings(_env_file=None))

    with TestClient(app) as client:
        response = client.post("/chat/ui", data={"message": "hello"})

    assert response.status_code == 503
    assert "Azure OpenAI chat is not configured." in response.text
    assert "AZURE_OPENAI_ENDPOINT" in response.text


def test_agent_ui_returns_missing_settings_fragment() -> None:
    app = create_app(settings=Settings(_env_file=None))

    with TestClient(app) as client:
        response = client.post("/agent/ui", data={"message": "hello"})

    assert response.status_code == 503
    assert "Azure OpenAI agent is not configured." in response.text
    assert "AZURE_OPENAI_ENDPOINT" in response.text
