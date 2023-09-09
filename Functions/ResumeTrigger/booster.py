from typing import List, Dict
from .resume_line import ResumeLine
from .gpt_api_caller import GptApiCaller
import tiktoken
import json
from .gpt_api_response import GptApiResponse


class Booster:
    TEMP = 0.2
    BULLET_POINT = '~'
    SYSTEM_PROMPT = "You're an expert career advisor. You've been helping improve people's resumes for 20 years."
    REPHRASE_PROMPT = f"Rephrase the following resume sentences in a concise, action oriented and " \
                      f"impressive manner to improve the overall quality of the resume:\n"
    # REPHRASE_PROMPT = f"Rewrite the following resume sentences in a concise, action-oriented and impressive manner to improve the overall" \
    #     f"quality of the resume. Use strong verbs, quantifiable results and specific skills to showcase my achievements and abilities." \
    #     f"Here are the lines to improve: \n"

    FEEDBACK_PROMPT = "Please analyze my resume and rate each of the following criteria out of 100:\n" \
                      "Clarity and readability\nRelevance\nAchievements\nKeywords\n" \
                      "Please provide specific examples with quotes from the text to support your ratings.\n" \
                      "After analyzing my resume, please provide a feedback that includes specific examples " \
                      "from the text to support your ratings. keep the feedback critical and respectful." \
                      "I am the applicant, talk to me directly."

    REPHRASE_FUNCTION = {
        "name": "get_feedback", "parameters": {
            "type": "object",
            "properties": {
                "lines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "old_line": {"type": "string", "description": "line from the prompt"},
                            "new_line": {"type": "string", "description": "The improved line"}
                        },
                        "required": ["old_line", "new_line"]
                    }
                },
                "number_of_lines": {"type": "integer", "description": "The number of lines"}
            },
            "required": ["lines"]
        }

    }

    FEEDBACK_FUNCTION = {"name": "get_feedback", "parameters": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "general feedback about the resume"
            },
            "clarity": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "feedback regarding clarity"},
                    "score": {"type": "integer", "description": "score out of 100"}
                }
            },
            "relevance": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "feedback regarding relevance"},
                    "score": {"type": "integer", "description": "score out of 100"}
                }
            },
            "achievements": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "feedback regarding achievements"},
                    "score": {"type": "integer", "description": "score out of 100"}
                }
            },
            "keywords": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "feedback regarding keywords"},
                    "score": {"type": "integer", "description": "score out of 100"}
                }
            },
        }
    }}

    DEFAULT_SCORE = 75
    CATEGORIES_TITLES = ['readability:',
                         'Relevance:', 'Achievements:', 'Keywords:']

    def __init__(self):
        self._edited_lines: List[Dict[str, str]] = []
        # self._score: Dict[str, int] = {}
        self._clarity = Dict[str, int | str]
        self._relevance = Dict[str, int | str]
        self._achievements = Dict[str, int | str]
        self._keywords = Dict[str, int | str]
        self._summary: str = ""
        self._gpt_caller: GptApiCaller = GptApiCaller()

    def _get_max_tokens(self, text) -> float:
        encoding = tiktoken.encoding_for_model(self._gpt_caller.MODEL_TYPE)
        return len(encoding.encode(text)) * 3

    @staticmethod
    def _format_lines_for_prompt(lines: List[ResumeLine]) -> str:
        return '\n'.join([f"line {index+1}: {line.text}\n" for index, line in enumerate(lines)])

    def _get_rephrase_lines_response(self, lines: List[ResumeLine]) -> GptApiResponse:
        messages = [self._gpt_caller.create_message(
            "system", self.SYSTEM_PROMPT)]
        all_lines = self._format_lines_for_prompt(lines)
        prompt = self.REPHRASE_PROMPT + f"{all_lines}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        max_tokens = self._get_max_tokens(all_lines)
        return self._gpt_caller.call_api(messages, self.TEMP, max_tokens, [self.REPHRASE_FUNCTION])

    def rephrase_lines(self, lines: List[ResumeLine]) -> List[ResumeLine]:
        api_res = self._get_rephrase_lines_response(lines)
        self.add_tokens(api_res)
        content = api_res.get_response_content()
        # sentences_list = [s.strip() for s in content.split('- ')[1:]]
        # self.add_lines_to_edited_lines(lines, sentences_list)
        self._edited_lines = json.loads(content)["lines"]
        return self._edited_lines

    def add_lines_to_edited_lines(self, resume_lines: List[ResumeLine], lines: List[str]) -> None:
        for line, resume_line in zip(lines, resume_lines):
            edited_line = {"old_line": resume_line.text, "new_line": line}
            self._edited_lines.append(edited_line)

    def _get_feedback_resume_response(self, resume_text: str) -> GptApiResponse:
        messages = [self._gpt_caller.create_message(
            "system", self.SYSTEM_PROMPT)]
        prompt = f"{self.FEEDBACK_PROMPT} {resume_text}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        max_tokens = self._get_max_tokens(resume_text)
        return self._gpt_caller.call_api(messages, self.TEMP, max_tokens, [self.FEEDBACK_FUNCTION])

    def feedback_resume(self, resume_text: str) -> any:
        api_res = self._get_feedback_resume_response(resume_text)
        return self.load_res(api_res)

    def load_res(self, api_res: GptApiResponse) -> any:
        self.add_tokens(api_res)
        res_text = api_res.get_response_content()
        res_dict = json.loads(res_text)
        self.extract_feedback(res_dict)
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

    def extract_feedback(self, res_dict: dict) -> None:
        self._clarity = res_dict["clarity"]
        self._relevance = res_dict["relevance"]
        self._achievements = res_dict["achievements"]
        self._keywords = res_dict["keywords"]
        self._summary = res_dict["summary"]

    def make_json(self) -> str:
        # edited_lines = [{"text": line.text, "start": (line.startX, line.startY), "end": (
        #     line.endX, line.endY)} for line in self._edited_lines]
        booster_dict = {"edited_lines": self._edited_lines,
                        "clarity": self._clarity,
                        "relevance": self._relevance,
                        "achievements": self._achievements,
                        "keywords": self._keywords,
                        "summary": self._summary,
                        }
        return json.dumps(booster_dict)
