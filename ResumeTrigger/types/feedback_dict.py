from typing import TypedDict

from ..constants import FEEDBACK_TYPE


class FeedbackData(TypedDict):
    feedback: str
    score: int


class FeedbackDict(TypedDict):
    feedback_type: FEEDBACK_TYPE
    data: FeedbackData


def default_feedback_dict(feedback_type: FEEDBACK_TYPE) -> FeedbackDict:
    return FeedbackDict(
        feedback_type=feedback_type, data=FeedbackData(feedback="", score=0)
    )
