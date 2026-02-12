from pydantic import BaseModel, Field


class AiAskRequest(BaseModel):
    question: str = Field(..., min_length=1)


class AiAskResponse(BaseModel):
    answer: str
    model: str
