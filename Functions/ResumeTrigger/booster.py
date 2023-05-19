from typing import List, Dict
import logging
import re
from .resume_line import ResumeLine
from .gpt_api_caller import GptApiCaller
import tiktoken
import json
from .gpt_api_response import GptApiResponse


class Booster:
    TEMP = 0.4
    BULLET_POINT = '~'
    SYSTEM_PROMPT = "You're an expert career advisor. You've been helping improve people's resumes for 20 years."
    REPHRASE_PROMPT = f"Rephrase the following resume sentences in a concise and " \
                      f"impressive manner to improve the overall quality of the resume:\n"
    FEEDBACK_PROMPT = "Please analyze my resume and rate each of the following criteria out of 100:\n" \
                      "Clarity and readability\nRelevance\nAchievements\nKeywords\n" \
                      "Please provide specific examples with quotes from the text to support your ratings.\n" \
                      "After analyzing my resume, please provide a feedback that includes specific examples " \
                      "from the text to support your ratings. keep the feedback critical and respectful." \
                      "I am the applicant, talk to me directly."

    DEFAULT_SCORE = 75
    CATEGORIES_TITLES = ['readability:',
                         'Relevance:', 'Achievements:', 'Keywords:']

    def __init__(self):
        self._edited_lines: List[Dict[str, str]] = []
        self._score: Dict[str, int] = {}
        self._clarity = ""
        self._relevance = ""
        self._achievements = ""
        self._keywords = ""
        self._feedback: str = ""
        self._gpt_caller: GptApiCaller = GptApiCaller()

    # def __str__(self):
    #     edited_lines_str = '\n'.join(
    #         [f'original: {line["original"]}, edited: {line["edited"]}' for line in self._edited_lines])
    #     # TODO change score print
    #     return f"Edited lines: {edited_lines_str}\nScore: {self._score}\nFeedback: " \
    #            f"{self._feedback}\nTokens used: {self._gpt_caller.tokens_used}"

    def rephrase_lines(self, lines: List[ResumeLine]) -> List[ResumeLine]:
        messages = [self._gpt_caller.create_message(
            "system", self.SYSTEM_PROMPT)]
        all_lines = '\n'.join([f"- {line.text}" for line in lines])
        prompt = self.REPHRASE_PROMPT + f"{all_lines}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        encoding = tiktoken.encoding_for_model(self._gpt_caller.MODEL_TYPE)
        max_tokens = len(encoding.encode(all_lines)) * 2
        api_res = self._gpt_caller.call_api(messages, self.TEMP, max_tokens)
        self.add_tokens(api_res)
        content = api_res.choices[0]["message"]["content"]
        logging.info(f"GPT response text: {content}")
        sentences_list = [s.strip() for s in content.split('- ')[1:]]
        self.add_lines_to_edited_lines(lines, sentences_list)

        return self._edited_lines

    def add_lines_to_edited_lines(self, resume_lines: List[ResumeLine], lines: List[str]) -> None:
        for line, resume_line in zip(lines, resume_lines):
            edited_line = {"old_line": resume_line.text, "new_line": line}
            self._edited_lines.append(edited_line)

    def feedback_resume(self, resume_text: str) -> any:
        messages = [self._gpt_caller.create_message(
            "system", self.SYSTEM_PROMPT)]
        prompt = f"{self.FEEDBACK_PROMPT} {resume_text}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        encoding = tiktoken.encoding_for_model(self._gpt_caller.MODEL_TYPE)
        max_tokens = len(encoding.encode(resume_text)) * 2
        api_res = self._gpt_caller.call_api(messages, self.TEMP, max_tokens)
        logging.info(f"GPT response text: {api_res}")
        return self.load_res(api_res)

    def load_res(self, api_res: GptApiResponse) -> any:
        self.add_tokens(api_res)
        res_text = api_res.choices[0].message.content
        logging.info(f"GPT response text: {res_text}")
        self.extract_score(res_text)
        self.extract_feedback(res_text)
        return self

    def add_tokens(self, api_res: GptApiResponse) -> any:
        self._gpt_caller.add_tokens(api_res.usage.total_tokens)
        return self

    def _check_if_title(self, words: List[str]):
        for category in self.CATEGORIES_TITLES:
            if category in words:
                return True

        return False

    def extract_score(self, text: str) -> None:
        result = {}
        for line in text.split('\n'):
            words = line.split(" ")
            if self._check_if_title(words):
                for i, word in enumerate(words):
                    if "/" in word:
                        result[words[0].rstrip(':').lower()] = int(
                            word.split('/')[0])
                        break

        self._score = result

    def extract_feedback(self, text: str) -> None:
        paragraphs = text.split('\n\n')
        self._clarity = paragraphs[0].split('\n')[1]
        self._relevance = paragraphs[1].split('\n')[1]
        self._achievements = paragraphs[2].split('\n')[1]
        self._keywords = paragraphs[3].split('\n')[1]
        self._feedback = paragraphs[4]

    def make_json(self) -> str:
        # edited_lines = [{"text": line.text, "start": (line.startX, line.startY), "end": (
        #     line.endX, line.endY)} for line in self._edited_lines]
        booster_dict = {"edited_lines": self._edited_lines,
                        "score": self._score,
                        "clarity": self._clarity,
                        "relevance": self._relevance,
                        "achievements": self._achievements,
                        "keywords": self._keywords,
                        "feedback": self._feedback,
                        }
        return json.dumps(booster_dict)
