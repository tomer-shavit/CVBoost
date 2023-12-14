from __future__ import annotations
from typing import List, Dict, Optional
from .types.feedback_dict import FeedbackDict, default_feedback_dict
from .resume_line import ResumeLine
from .gpt_api_caller import GptApiCaller
import tiktoken
import json
from .gpt_api_response import GptApiResponse
from .db_query import DBQuery
from .constants import *


class Booster:
    TEMP = 0.1
    SYSTEM_PROMPT = "You're an expert career advisor. You've been helping improve people's resumes for 20 years."
    REPHRASE_PROMPT = f"Rephrase the following resume sentences in a concise, action oriented and " \
                      f"impressive manner to improve the overall quality of the resume:\n"

    FEEDBACK_PROMPT = "Please analyze my resume and rate each of the following criteria out of 100:\n" \
                      "Clarity and readability\nRelevance\nAchievements\nKeywords\n" \
                      "Please provide specific examples with quotes from the text to support your ratings.\n" \
                      "Keep the feedback critical, respectful, and full of examples and quotes from the resume." \
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
                "description": "Summarize all the feedback into 4-5 lines. I am the applicant, talk to me directly."
            },
            "clarity": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "How easy is it to read the resume? Is the information presented in a logical order? Is there anything that i can do to improve it? Give examples with quotes. I am the applicant"},
                    "score": {"type": "integer", "description": "score out of 100 based on how clear the resume is"}
                }
            },
            "relevance": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "Are the skills and experience listed on the resume relevant to the job I'm applying for? Is there any irrelevant information that should be removed? Give examples with quotes. I am the applicant"},
                    "score": {"type": "integer", "description": "score out of 100 based on how relevant the resume is"}
                }
            },
            "achievements": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "How well have my accomplishments been highlighted? Are they quantifiable and well-described? What should i change to improve it? Give examples with quotes. I am the applicant"},
                    "score": {"type": "integer", "description": "score out of 100 based on well my accomplishments are highlighted"}
                }
            },
            "keywords": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "Have I included industry-specific keywords that will make my resume stand out to employers and applicant tracking systems? What should i change to improve it? Give examples with quotes. I am the applicant"},
                    "score": {"type": "integer", "description": "score out of 100 based on the amount of keywords used the resume"}
                }
            },
        }
    }}

    def __init__(self, user_id: str, resume_text:str ,db_query:DBQuery) -> None:
        self._user_id = user_id
        self._edited_lines: List[Dict[str, str]] = []
        self._clarity: FeedbackDict = default_feedback_dict()
        self._relevance: FeedbackDict = default_feedback_dict()
        self._achievements: FeedbackDict = default_feedback_dict()
        self._keywords: FeedbackDict = default_feedback_dict()
        self._summary: str = ""
        self.already_boosted = False

        self._gpt_caller: GptApiCaller = GptApiCaller()
        self._db = db_query
        self.boost_id = self.save_boost_to_db(resume_text)

    def _get_max_tokens(self, text) -> float:
        encoding = tiktoken.encoding_for_model(self._gpt_caller.MODEL_TYPE)
        return len(encoding.encode(text)) * 3

    @staticmethod
    def _format_lines_for_prompt(lines: List[ResumeLine]) -> str:
        return '\n'.join([f"line {index+1}: {line.text}\n" for index, line in enumerate(lines)])

    def _get_rephrase_lines_response(self, lines: List[ResumeLine]) -> Optional[GptApiResponse]:
        messages = [self._gpt_caller.create_message( "system", self.SYSTEM_PROMPT)]
        all_lines = self._format_lines_for_prompt(lines)
        prompt = self.REPHRASE_PROMPT + f"{all_lines}"

        messages.append((self._gpt_caller.create_message("user", prompt)))
        max_tokens = self._get_max_tokens(all_lines)
        
        return self._gpt_caller.call_api(messages, self.TEMP, int(max_tokens), [self.REPHRASE_FUNCTION])

    def rephrase_lines(self, lines: List[ResumeLine]) -> List[Dict[str, str]]:
        api_res = self._get_rephrase_lines_response(lines)
        
        if not api_res:
            raise Exception("Failed to get response model.")

        self.add_tokens(api_res)
        content = api_res.get_response_content()
        self._edited_lines = json.loads(content)["lines"]
        self.save_lines_to_db()

        return self._edited_lines

    def _get_feedback_resume_response(self, resume_text: str) -> Optional[GptApiResponse]:
        messages = [self._gpt_caller.create_message(
            "system", self.SYSTEM_PROMPT)]
        prompt = f"{self.FEEDBACK_PROMPT} {resume_text}"
        messages.append((self._gpt_caller.create_message("user", prompt)))
        max_tokens = self._get_max_tokens(resume_text)

        return self._gpt_caller.call_api(messages, self.TEMP, int(max_tokens), [self.FEEDBACK_FUNCTION])

    def feedback_resume(self, resume_text: str) -> Booster:
        api_res = self._get_feedback_resume_response(resume_text)
       
        if not api_res:
            raise Exception("Failed to get response model.")

        self.load_res(api_res)
        self.save_feedbacks_to_db()

        return self

    def load_res(self, api_res: GptApiResponse) -> Booster:
        self.add_tokens(api_res)
        res_text = api_res.get_response_content()
        res_dict = json.loads(res_text)
        self.extract_feedback(res_dict)
        
        return self

    def add_tokens(self, api_res: GptApiResponse) -> Booster:
        self._gpt_caller.add_tokens(api_res.usage.total_tokens)  # type: ignore[attr-defined]
        
        return self

    def extract_feedback(self, res_dict: dict) -> None:
        self._clarity = res_dict["clarity"]
        self._relevance = res_dict["relevance"]
        self._achievements = res_dict["achievements"]
        self._keywords = res_dict["keywords"]
        self._summary = res_dict["summary"]

    def make_json(self) -> str:
        booster_dict = {"boost_id": self.boost_id,
                        "edited_lines": self._edited_lines,
                        "clarity": self._clarity,
                        "relevance": self._relevance,
                        "achievements": self._achievements,
                        "keywords": self._keywords,
                        "summary": self._summary,
                        }
        
        return json.dumps(booster_dict)
    
    def decrease_boost(self) -> bool:
        return self._db.decrease_boost(self._user_id)
    
    def delete_boost(self) -> bool:
        return self._db.delete_boost(self.boost_id)

    def save_boost_to_db(self, resume_text:str) -> int:
        maybe_boost_id =  self.check_already_boosted(resume_text)
        if maybe_boost_id:
            self.already_boosted = True
            return maybe_boost_id

        boost_id = self._db.insert_resume_boost(self._user_id, BoostVersion.V1, resume_text)

        return boost_id if boost_id else -1 

    def save_feedbacks_to_db(self) -> bool:
        if self.boost_id == -1:
            return False

        status = True
        status = status and self._db.insert_feedback(self.boost_id, FEEDBACK_TYPE.CLARITY, self._clarity["feedback"], self._clarity["score"], is_liked=False)
        status = status and self._db.insert_feedback(self.boost_id, FEEDBACK_TYPE.RELEVANCE, self._relevance["feedback"], self._relevance["score"], is_liked=False)
        status = status and self._db.insert_feedback(self.boost_id, FEEDBACK_TYPE.ACHIEVEMENTS, self._achievements["feedback"], self._achievements["score"], is_liked=False)
        status = status and self._db.insert_feedback(self.boost_id, FEEDBACK_TYPE.KEYWORDS, self._keywords["feedback"], self._keywords["score"], is_liked=False)
        status = status and self._db.insert_feedback(self.boost_id, FEEDBACK_TYPE.SUMMARY, self._summary, 0, is_liked=False)

        return status

    
    def save_lines_to_db(self) -> bool:
        for line in self._edited_lines:
            status = self._db.insert_line_feedback(boost_id=self.boost_id, 
                                                   feedback_type=FEEDBACK_TYPE.REPHRASE, 
                                                   feedback_text=line["new_line"], 
                                                   is_liked=False, 
                                                   feedback_text_reference=line["old_line"])
            if not status:
                return False

        return status

    def check_already_boosted(self, resume_text:str) -> int | None:
        boost = self._db.get_boost_by_hash(resume_text)
        if not boost:
            return None

        self._db.set_salt(boost["salt"])
        return boost["boostId"]
    
    def is_already_boosted(self) -> bool:
        return self.already_boosted
    
    def recall_feedback(self) -> Booster:
        feedbacks = self._db.get_feedbacks(self.boost_id)
        
        for feedback in feedbacks:
            if feedback['feedbackType'] == FEEDBACK_TYPE.REPHRASE:
                self._edited_lines.append({"old_line": self._db.decrypt_sensative_text(feedback["feedbackTextReference"]), 
                                           "new_line": self._db.decompress_text(feedback["feedbackText"])})
            
            elif feedback['feedbackType'] == FEEDBACK_TYPE.CLARITY:
                self._clarity = FeedbackDict(feedback=self._db.decompress_text(feedback["feedbackText"]), score=feedback["score"])

            elif feedback['feedbackType'] == FEEDBACK_TYPE.RELEVANCE:
                self._relevance = FeedbackDict(feedback=self._db.decompress_text(feedback["feedbackText"]), score=feedback["score"])
                
            elif feedback['feedbackType'] == FEEDBACK_TYPE.ACHIEVEMENTS:
                self._achievements = FeedbackDict(feedback=self._db.decompress_text(feedback["feedbackText"]), score=feedback["score"])
                
            elif feedback['feedbackType'] == FEEDBACK_TYPE.KEYWORDS:
                self._keywords = FeedbackDict(feedback=self._db.decompress_text(feedback["feedbackText"]), score=feedback["score"])

            elif feedback['feedbackType'] == FEEDBACK_TYPE.SUMMARY:
                self._summary = self._db.decompress_text(feedback["feedbackText"])

        return self

