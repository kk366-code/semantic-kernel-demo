from fastapi.testclient import TestClient

from semantic_kernel_api.config import Settings
from semantic_kernel_api.main import create_app


class FakeAgentService:
    async def complete(self, message: str) -> str:
        return f"Agent: {message}"


def test_agent_returns_answer_from_injected_service() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        agent_service=FakeAgentService(),
    )

    with TestClient(app) as client:
        response = client.post("/agent", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Agent: hello",
        "agent_name": "ProjectGuideAgent",
    }


def test_agent_returns_503_when_azure_chat_is_not_configured() -> None:
    app = create_app(settings=Settings(_env_file=None))

    with TestClient(app) as client:
        response = client.post("/agent", json={"message": "hello"})

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "message": "Azure OpenAI agent is not configured.",
            "missing_settings": [
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_CHAT_DEPLOYMENT",
            ],
        }
    }


def test_agent_rejects_empty_message() -> None:
    app = create_app(
        settings=Settings(_env_file=None),
        agent_service=FakeAgentService(),
    )

    with TestClient(app) as client:
        response = client.post("/agent", json={"message": ""})

    assert response.status_code == 422
