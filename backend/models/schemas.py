from enum import Enum
from pydantic import BaseModel


# Pydantic schemas for the chat API.
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class Intent(str, Enum):
    TASK = "task"
    CALENDAR = "calendar"
    NOTES = "notes"
    PLAN_DAY = "plan_day"
