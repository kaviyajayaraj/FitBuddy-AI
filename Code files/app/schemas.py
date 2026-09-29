from pydantic import BaseModel, Field
from typing import Literal

class UserInput(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    user_id: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=0, le=500)
    goal: str
    intensity: Literal["Low", "Medium", "High"]

class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str = Field(min_length=3, max_length=1000)
