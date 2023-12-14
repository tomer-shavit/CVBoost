from typing import TypedDict


class EditedLineFeedback(TypedDict):
    feedbackId: int
    old_line: str
    new_line: str

