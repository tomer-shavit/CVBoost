
from typing import TypedDict

class FeedbackDict(TypedDict):
    feedbackId: int 
    feedback: str
    score: int
    
def default_feedback_dict() -> FeedbackDict:
    return FeedbackDict(feedbackId=0, feedback="", score=0)