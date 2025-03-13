from typing import TypedDict, List

from ..constants import FEEDBACK_TYPE


class EditedLine(TypedDict):
    old_line: str
    new_line: str


class EditedLineFeedback(TypedDict):
    feedback_type: FEEDBACK_TYPE
    data: EditedLine
