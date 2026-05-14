from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    answer: str


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class AgentResponse(BaseModel):
    answer: str
    agent_name: str
