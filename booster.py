from typing import List

from resume_line import ResumeLine
from gpt_api_caller import GptApiCaller


class Booster:
    TEMP = 0.6
    SYSTEM_MSG = "You're an expert career advisor. You've been helping improve people's resumes for 20 years."
    def __init__(self):
        self._original_text: str = ""
        self._lines_to_edit: List[ResumeLine] = []
        self._edited_lines: List[ResumeLine] = []
        self._score: float = -1
        self._summary: str = ""
        self._gpt_caller: GptApiCaller = GptApiCaller()

    def rephrase_line(self, line: ResumeLine) -> ResumeLine:
        pass

    def rate_resume(self, resume_text: str) -> float:
        pass

    def gen_pros_and_cons(self, resume_text: str) -> str:
        pass
