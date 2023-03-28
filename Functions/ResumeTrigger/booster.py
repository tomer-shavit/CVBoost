from typing import List, Self
import re
from .resume_line import ResumeLine
from .gpt_api_caller import GptApiCaller
import tiktoken
import json
from .gpt_api_response import GptApiResponse


class Booster:
    TEMP = 0.5
    BULLET_POINT = '~'
    SYSTEM_PROMPT = "You're an expert career advisor. You've been helping improve people's resumes for 20 years."
    FEEDBACK_PROMPT = f"I am the applicant, talk to me directly. Rate my resume out of 100," \
                      f" respond only with the number. Then write a mostly positive yet critical feedback paragraph" \
                      f" on it. Then, without saying anything else, " \
                      f"give 3-4 bullet points that start with {BULLET_POINT} on how to improve it:"
    DEFAULT_SCORE = 75

    def __init__(self):
        self._edited_lines: List[ResumeLine] = []
        self._score: int = -1
        self._feedback: str = ""
        self._bullet_points: List[str] = []
        self._gpt_caller: GptApiCaller = GptApiCaller()

    def __str__(self):
        edited_lines_str = '\n'.join(
            [f'original: {line["original"]}, edited: {line["edited"]}' for line in self._edited_lines])
        return f"Edited lines: {edited_lines_str}\nScore: {self._score}\nFeedback: " \
               f"{self._feedback}\nBullet Points:{self._bullet_points}\nTokens used: {self._gpt_caller.tokens_used}"

    def rephrase_line(self, line: ResumeLine) -> ResumeLine:
        messages = [self._gpt_caller.create_message(
            "system", self.SYSTEM_PROMPT)]
        prompt = f"Rephrase this sentence in an impressive, short and sweet way: {line.text}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        encoding = tiktoken.encoding_for_model(self._gpt_caller.MODEL_TYPE)
        max_tokens = len(encoding.encode(line.text))
        api_res = self._gpt_caller.call_api(messages, self.TEMP, max_tokens)
        self.add_tokens(api_res)
        edited_line = ResumeLine(api_res.choices[0]["message"]["content"], line.startX, line.endX, line.startY,
                                 line.endY)
        self._edited_lines.append(edited_line)
        return edited_line

    def feedback_resume(self, resume_text: str) -> any:
        messages = [self._gpt_caller.create_message(
            "system", self.SYSTEM_PROMPT)]
        prompt = f"{self.FEEDBACK_PROMPT} {resume_text}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        encoding = tiktoken.encoding_for_model(self._gpt_caller.MODEL_TYPE)
        max_tokens = len(encoding.encode(resume_text))
        api_res = self._gpt_caller.call_api(messages, self.TEMP, max_tokens)
        return self.load_res(api_res)

    def load_res(self, api_res: GptApiResponse) -> any:
        self.add_tokens(api_res)
        res_text = api_res.choices[0].message.content
        res_text = self.extract_score(res_text)
        res_text = self.extract_feedback(res_text)
        self.get_bullets(res_text)
        return self

    def add_tokens(self, api_res: GptApiResponse) -> any:
        self._gpt_caller.add_tokens(api_res.usage.total_tokens)
        return self

    def extract_score(self, res_text: str) -> str:
        grade_str = ""
        if res_text[0].isdigit():
            grade_str = re.search(r'\d+', res_text).group()
            self._score = int(grade_str)
        else:
            self._score = self.DEFAULT_SCORE

        return res_text.lstrip(grade_str)

    def extract_feedback(self, res_text: str) -> str:
        text_split = res_text.split(self.BULLET_POINT)
        self._feedback = text_split[0].strip('\n')
        return "".join(text_split[1:])

    def get_bullets(self, res_text: str) -> None:
        text_split = res_text.split('\n')
        for bullet in text_split:
            if len(bullet):
                self._bullet_points.append(bullet.strip())

    def make_json(self) -> str:
        edited_lines = [{"text": line.text, "start": (line.startX, line.startY), "end": (
            line.endX, line.endY)} for line in self._edited_lines]
        booster_dict = {"score": self._score, "edited_lines": edited_lines,
                        "feedback": self._feedback, "bullet_points": self._bullet_points}
        return json.dumps(booster_dict)
