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
from .db_query import DBQuery
from .gpt_api_caller import GptApiCaller
from .gpt_api_response import GptApiResponse
from .resume_line import ResumeLine
from .types.feedback_dict import FeedbackDict, default_feedback_dict
from .types.edited_lines import EditedLineFeedback


class Booster:
    TEMP_GPT4 = 0
    TEMP_GPT3 = 0.1

    def __init__(self, user_id: str, resume_text: str, db_query: DBQuery) -> None:
        self._user_id = user_id
        self._edited_lines: List[EditedLineFeedback] = []
        self._clarity: FeedbackDict = default_feedback_dict()
        self._relevance: FeedbackDict = default_feedback_dict()
        self._achievements: FeedbackDict = default_feedback_dict()
        self._keywords: FeedbackDict = default_feedback_dict()
        self._summary: FeedbackDict = default_feedback_dict()
        self.already_boosted = False
        self._gpt_caller: GptApiCaller = GptApiCaller()

        self._prompt_factory: PromptFactory = PromptFactory()
        self._db = db_query
        self.boost_id = self.save_boost_to_db(resume_text)

    def _get_max_tokens(self, text, model_type) -> float:
        encoding = tiktoken.encoding_for_model(model_type)
        return len(encoding.encode(text)) * 3

    @staticmethod
    def _format_lines_for_prompt(lines: List[ResumeLine]) -> str:
        return "\n".join(
            [f"line {index+1}: {line.text}\n" for index, line in enumerate(lines)]
        )

    def _get_rephrase_lines_response(
        self, lines: List[ResumeLine]
    ) -> Optional[GptApiResponse]:
        system_prompt = self._prompt_factory.build_system_prompt(SystemType.BOOST)
        messages = [self._gpt_caller.create_message("system", system_prompt)]
        all_lines = self._format_lines_for_prompt(lines)
        prompt = self._prompt_factory.build_repharse_prompt() + f"{all_lines}"
        model_type = self._gpt_caller.GPT3
        messages.append((self._gpt_caller.create_message("user", prompt)))
        max_tokens = self._get_max_tokens(all_lines, model_type)

        return self._gpt_caller.call_api(
            messages,
            self.TEMP_GPT3,
            int(max_tokens),
            model_type,
            [self._prompt_factory.build_rephrase_function()],
        )

    def rephrase_lines(self, lines: List[ResumeLine]) -> List[EditedLineFeedback]:
        api_res = self._get_rephrase_lines_response(lines)

        if not api_res:
            raise Exception("Failed to get response model.")

        self.add_tokens(api_res)
        content = api_res.get_response_content()
        self._edited_lines = json.loads(content)["lines"]
        self.save_lines_to_db()

        return self._edited_lines

    def _get_feedback_resume_response(
        self, resume_text: str, model_type: str, temp_type: float
    ) -> Optional[GptApiResponse]:
        system_prompt = self._prompt_factory.build_system_prompt(SystemType.BOOST)
        messages = [self._gpt_caller.create_message("system", system_prompt)]

        if model_type == self._gpt_caller.GPT4:
            prompt = f"{resume_text}"
        else:
            prompt = f"{self._prompt_factory.build_feedback_prompt(BoostVersion.V1)} {resume_text}"

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

    def feedback_resume(self, resume_text: str) -> Booster:
        api_res = self._get_feedback_resume_response(
            resume_text, self._gpt_caller.GPT4, self.TEMP_GPT4
        )

        isFeedbackGood = self.load_res(api_res)
        if not isFeedbackGood:
            api_res = self._get_feedback_resume_response(
                resume_text, self._gpt_caller.GPT3, self.TEMP_GPT3
            )
            self.load_res(api_res)

        self.save_feedbacks_to_db()

        return self

    def load_res(self, api_res: Union[GptApiResponse, None]) -> bool:
        if not api_res:
            raise Exception("Failed to get response model.")

        self.add_tokens(api_res)
        res_text = api_res.get_response_content()
        res_dict = json.loads(res_text)
        if "Please provide" in res_dict["summary"]:
            return False
        self.extract_feedback(res_dict)

        return True

    def add_tokens(self, api_res: GptApiResponse) -> Booster:
        self._gpt_caller.add_tokens(api_res.usage.total_tokens)  # type: ignore[attr-defined]

        return self

    def extract_feedback(self, res_dict: dict) -> None:
        self._clarity = res_dict["clarity"]
        self._relevance = res_dict["relevance"]
        self._achievements = res_dict["achievements"]
        self._keywords = res_dict["keywords"]
        self._summary["feedback"] = res_dict["summary"]

    def make_json(self) -> str:
        booster_dict = {
            "boost_id": self.boost_id,
            "edited_lines": self._edited_lines,
            "clarity": self._clarity,
            "relevance": self._relevance,
            "achievements": self._achievements,
            "keywords": self._keywords,
            "summary": self._summary,
        }

        return json.dumps(booster_dict)

    def decrease_boost(self) -> bool:
        try:
            self._db.decrease_boost(self._user_id)

        except Exception as e:
            print("Error in Booster.decrease_boost(): ", e)
            return False

        return True

    def delete_boost(self) -> bool:
        try:
            self._db.delete_boost(self.boost_id)

        except Exception as e:
            print("Error in Booster.delete_boost(): ", e)
            return False

        return True

    def save_boost_to_db(self, resume_text: str) -> int:
        maybe_boost_id = self.check_already_boosted(resume_text)

        if maybe_boost_id:
            self.already_boosted = True
            return maybe_boost_id

        boost_id = self._db.insert_resume_boost(
            self._user_id, BoostVersion.V1, resume_text
        )

        return boost_id

    def save_feedbacks_to_db(self) -> bool:
        if self.boost_id == -1:
            return False

        try:
            self._clarity["feedbackId"] = self._db.insert_feedback(
                self.boost_id,
                FEEDBACK_TYPE.CLARITY,
                self._clarity["feedback"],
                self._clarity["score"],
                is_liked=False,
            )
            self._relevance["feedbackId"] = self._db.insert_feedback(
                self.boost_id,
                FEEDBACK_TYPE.RELEVANCE,
                self._relevance["feedback"],
                self._relevance["score"],
                is_liked=False,
            )
            self._achievements["feedbackId"] = self._db.insert_feedback(
                self.boost_id,
                FEEDBACK_TYPE.ACHIEVEMENTS,
                self._achievements["feedback"],
                self._achievements["score"],
                is_liked=False,
            )
            self._keywords["feedbackId"] = self._db.insert_feedback(
                self.boost_id,
                FEEDBACK_TYPE.KEYWORDS,
                self._keywords["feedback"],
                self._keywords["score"],
                is_liked=False,
            )
            self._summary["feedbackId"] = self._db.insert_feedback(
                self.boost_id,
                FEEDBACK_TYPE.SUMMARY,
                self._summary["feedback"],
                0,
                is_liked=False,
            )

        except Exception as e:
            print("Error in Booster.save_feedbacks_to_db(): ", e)
            self.delete_boost()
            return False

        return True

    def save_lines_to_db(self) -> bool:
        try:
            for line in self._edited_lines:
                line["feedbackId"] = self._db.insert_line_feedback(
                    boost_id=self.boost_id,
                    feedback_type=FEEDBACK_TYPE.REPHRASE,
                    feedback_text=line["new_line"],
                    is_liked=False,
                    feedback_text_reference=line["old_line"],
                )

        except Exception as e:
            print("Error in Booster.save_lines_to_db(): ", e)
            self.delete_boost()
            return False

        return True

    def check_already_boosted(self, resume_text: str) -> int | None:
        boost = self._db.get_boost_by_hash(resume_text)
        if not boost:
            return None

        return boost["boostId"]

    def is_already_boosted(self) -> bool:
        return self.already_boosted

    def recall_feedback(self) -> Booster:
        feedbacks = self._db.get_feedbacks(self.boost_id)

        for feedback in feedbacks:
            if feedback["feedbackType"] == FEEDBACK_TYPE.REPHRASE:
                self._edited_lines.append(
                    EditedLineFeedback(
                        feedbackId=feedback["feedbackId"],
                        old_line=self._db.decrypt_text(
                            feedback["feedbackTextReference"]
                        ),
                        new_line=self._db.decrypt_text(feedback["feedbackText"]),
                    )
                )

            elif feedback["feedbackType"] == FEEDBACK_TYPE.CLARITY:
                self._clarity = FeedbackDict(
                    feedbackId=feedback["feedbackId"],
                    feedback=self._db.decrypt_text(feedback["feedbackText"]),
                    score=feedback["score"],
                )

            elif feedback["feedbackType"] == FEEDBACK_TYPE.RELEVANCE:
                self._relevance = FeedbackDict(
                    feedbackId=feedback["feedbackId"],
                    feedback=self._db.decrypt_text(feedback["feedbackText"]),
                    score=feedback["score"],
                )

            elif feedback["feedbackType"] == FEEDBACK_TYPE.ACHIEVEMENTS:
                self._achievements = FeedbackDict(
                    feedbackId=feedback["feedbackId"],
                    feedback=self._db.decrypt_text(feedback["feedbackText"]),
                    score=feedback["score"],
                )

            elif feedback["feedbackType"] == FEEDBACK_TYPE.KEYWORDS:
                self._keywords = FeedbackDict(
                    feedbackId=feedback["feedbackId"],
                    feedback=self._db.decrypt_text(feedback["feedbackText"]),
                    score=feedback["score"],
                )

            elif feedback["feedbackType"] == FEEDBACK_TYPE.SUMMARY:
                self._summary = FeedbackDict(
                    feedbackId=feedback["feedbackId"],
                    feedback=self._db.decrypt_text(feedback["feedbackText"]),
                    score=feedback["score"],
                )
        return self
