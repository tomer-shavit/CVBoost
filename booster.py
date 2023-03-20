from typing import List

from resume_line import ResumeLine
from gpt_api_caller import GptApiCaller
import tiktoken


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
        messages = [self._gpt_caller.create_message("system", self.SYSTEM_MSG)]
        prompt = f"Rephrase this sentence in an impressive, short and sweet way: {line.text}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        encoding = tiktoken.encoding_for_model(self._gpt_caller.MODEL_TYPE)
        max_tokens = len(encoding.encode(line.text))
        api_res = self._gpt_caller.call_api(messages, self.TEMP, max_tokens)
        return ResumeLine(api_res.choices[0]["message"]["content"], line.startX, line.endX, line.startY, line.endY)

    def rate_resume(self, resume_text: str) -> float:
        messages = [self._gpt_caller.create_message("system", self.SYSTEM_MSG)]
        prompt = f"rate this resume out of 100, rank it based on the way that it was written and not by its content" \
                 f", respond only with the number: {resume_text}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        encoding = tiktoken.encoding_for_model(self._gpt_caller.MODEL_TYPE)
        max_tokens = len(encoding.encode(resume_text))
        api_res = self._gpt_caller.call_api(messages, self.TEMP, max_tokens)
        print(api_res)
        return 0





    def gen_pros_and_cons(self, resume_text: str) -> str:
        pass
