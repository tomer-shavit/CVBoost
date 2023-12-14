
from typing import TypedDict

class FeedbackDict(TypedDict):
    feedback: str
    score: int
    
def default_feedback_dict() -> FeedbackDict:
    return FeedbackDict(feedback="", score=0)