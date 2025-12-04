from pydantic import BaseModel
from typing import List, Literal


class AskRequest(BaseModel):
    query: str
    mode: Literal["answer", "email", "summary"] = "answer"


class AskResponse(BaseModel):
    mode: str
    answer: str
    citations: List[str] = []
