from __future__ import annotations

import json
from typing import List, Optional, Union

import tiktoken


from .prompt_factory import (
    BoostVersion,
    PromptFactory,
    SystemType,
)

from .constants import *
from .gpt_api_caller import GptApiCaller
from .gpt_api_response import GptApiResponse
from .types.feedback_dict import FeedbackDict, default_feedback_dict
from .types.edited_lines import EditedLine, EditedLineFeedback


class Booster:
    TEMP_GPT4 = 0
    TEMP_GPT3 = 0.1

    def __init__(self, user_id: str, resume_text: str) -> None:
        self._user_id = user_id
        self._edited_lines: List[EditedLineFeedback] = []
        self._clarity: FeedbackDict = default_feedback_dict(FEEDBACK_TYPE.CLARITY)
        self._relevance: FeedbackDict = default_feedback_dict(FEEDBACK_TYPE.RELEVANCE)
        self._achievements: FeedbackDict = default_feedback_dict(
            FEEDBACK_TYPE.ACHIEVEMENTS
        )
        self._keywords: FeedbackDict = default_feedback_dict(FEEDBACK_TYPE.KEYWORDS)
        self._summary: FeedbackDict = default_feedback_dict(FEEDBACK_TYPE.SUMMARY)
        self.already_boosted = False
        self.resume_text = resume_text
        self._gpt_caller: GptApiCaller = GptApiCaller()

        self._prompt_factory: PromptFactory = PromptFactory()

    def _get_max_tokens(self, text, model_type) -> float:
        encoding = tiktoken.encoding_for_model(model_type)
        return len(encoding.encode(text)) * 3

    def _get_rephrase_lines_response(
        self, resume_text: str
    ) -> Optional[GptApiResponse]:
        system_prompt = self._prompt_factory.build_system_prompt(SystemType.BOOST)
        messages = [self._gpt_caller.create_message("system", system_prompt)]
        prompt = self._prompt_factory.build_repharse_prompt() + f"{resume_text}"
        model_type = self._gpt_caller.GPT4
        messages.append((self._gpt_caller.create_message("user", prompt)))
        max_tokens = self._get_max_tokens(resume_text, model_type)

        return self._gpt_caller.call_api(
            messages,
            self.TEMP_GPT4,
            int(max_tokens),
            model_type,
            [self._prompt_factory.build_rephrase_function()],
        )

    @staticmethod
    def build_lines_form_response(lines_data) -> List[EditedLineFeedback]:
        lines = []
        for line in lines_data:
            lines.append(
                EditedLineFeedback(
                    feedback_type=FEEDBACK_TYPE.REPHRASE,
                    data=EditedLine(
                        old_line=line["old_line"], new_line=line["new_line"]
                    ),
                )
            )

        return lines

    def rephrase_lines(self) -> List[EditedLineFeedback]:
        api_res = self._get_rephrase_lines_response(self.resume_text)

        if not api_res:
            raise Exception("Failed to get response model.")

        self.add_tokens(api_res)
        content = api_res.get_response_content()
        lines_data = json.loads(content)["lines"]
        self._edited_lines = self.build_lines_form_response(lines_data)

        return self._edited_lines

    def _get_feedback_resume_response(
        self, resume_text: str, model_type: str, temp_type: float
    ) -> Optional[GptApiResponse]:
        system_prompt = self._prompt_factory.build_system_prompt(SystemType.BOOST)
        messages = [self._gpt_caller.create_message("system", system_prompt)]

        if model_type == self._gpt_caller.GPT4:
            prompt = f"Follow the instuctions in the get_feedback function about this resume: {resume_text}"
        else:
            prompt = f"{self._prompt_factory.build_feedback_prompt(BoostVersion.V1)} {resume_text}"

        messages.append((self._gpt_caller.create_message("user", prompt)))
        max_tokens = self._get_max_tokens(resume_text, model_type)

        return self._gpt_caller.call_api(
            messages,
            temp_type,
            int(max_tokens),
            model_type,
            [self._prompt_factory.build_feedback_function()],
        )

    def feedback_resume(self) -> Booster:
        api_res = self._get_feedback_resume_response(
            self.resume_text, self._gpt_caller.GPT4, self.TEMP_GPT4
        )
        self.load_res(api_res)

        return self

    def load_res(self, api_res: Union[GptApiResponse, None]) -> bool:
        if not api_res:
            raise Exception("Failed to get response model.")

        self.add_tokens(api_res)
        res_text = api_res.get_response_content()
        res_dict = json.loads(res_text)
        self.extract_feedback(res_dict)

        return True

    def add_tokens(self, api_res: GptApiResponse) -> Booster:
        self._gpt_caller.add_tokens(api_res.usage.total_tokens)  # type: ignore[attr-defined]

        return self

    def extract_feedback(self, res_dict: dict) -> None:
        self._clarity["data"] = res_dict["clarity"]
        self._relevance["data"] = res_dict["relevance"]
        self._achievements["data"] = res_dict["achievements"]
        self._keywords["data"] = res_dict["keywords"]
        self._summary["data"]["feedback"] = res_dict["summary"]

    def make_json(self) -> str:
        booster_dict = {
            "edited_lines": self._edited_lines,
            "clarity": self._clarity,
            "relevance": self._relevance,
            "achievements": self._achievements,
            "keywords": self._keywords,
            "summary": self._summary,
            "resume_text": self.resume_text,
        }

        return json.dumps(booster_dict)
