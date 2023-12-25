from enum import IntEnum

from .types.feedback_function import FeedbackFunction

from .types.rephrase_functions import RephraseFunction


class SystemType(IntEnum):
    BOOST = 1


class BoostVersion(IntEnum):
    V1 = 1


class PromptFactory:
    def __init__(self) -> None:
        pass

    @staticmethod
    def build_system_prompt(type: SystemType) -> str:
        if type == SystemType.BOOST:
            return "You're an expert career advisor. You've been helping improve people's resumes for 20 years. output JSON"

    @staticmethod
    def build_feedback_prompt(version: BoostVersion) -> str:
        if version == BoostVersion.V1:
            return (
                "Please analyze my resume and rate each of the following criteria out of 100:\n"
                "Clarity and readability\nRelevance\nAchievements\nKeywords\n"
                "Please provide specific examples with quotes from the text to support your ratings.\n"
                "Keep the feedback critical, respectful, and full of examples and quotes from the resume."
                "I am the applicant, talk to me directly."
            )

    @staticmethod
    def build_feedback_function() -> FeedbackFunction:
        return {
            "name": "get_feedback",
            "parameters": {
                "type": "object",
                "properties": {
                    "clarity": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": "How easy is it to read the resume? Is the information presented in a logical order? Is there anything that i can do to improve it? Give examples with quotes. I am the applicant",
                            },
                            "score": {
                                "type": "integer",
                                "description": "score out of 100 based on how clear the resume is",
                            },
                        },
                    },
                    "relevance": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": "Are the skills and experience listed on the resume relevant to the job I'm applying for? Is there any irrelevant information that should be removed? Give examples with quotes. I am the applicant",
                            },
                            "score": {
                                "type": "integer",
                                "description": "score out of 100 based on how relevant the resume is",
                            },
                        },
                    },
                    "achievements": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": "How well have my accomplishments been highlighted? Are they quantifiable and well-described? What should i change to improve it? Give examples with quotes. I am the applicant",
                            },
                            "score": {
                                "type": "integer",
                                "description": "score out of 100 based on well my accomplishments are highlighted",
                            },
                        },
                    },
                    "keywords": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": "Have I included industry-specific keywords that will make my resume stand out to employers and applicant tracking systems? What should i change to improve it? Give examples with quotes. I am the applicant",
                            },
                            "score": {
                                "type": "integer",
                                "description": "score out of 100 based on the amount of keywords used the resume",
                            },
                        },
                    },
                },
            },
        }

    @staticmethod
    def build_repharse_prompt() -> str:
        return (
            f"Rephrase the following resume sentences in a concise, action oriented and "
            f"impressive manner to improve the overall quality of the resume:\n"
        )

    @staticmethod
    def build_rephrase_function() -> RephraseFunction:
        return {
            "name": "get_feedback",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "old_line": {
                                    "type": "string",
                                    "description": "line from the prompt",
                                },
                                "new_line": {
                                    "type": "string",
                                    "description": "The improved line",
                                },
                            },
                            "required": ["old_line", "new_line"],
                        },
                    },
                    "number_of_lines": {
                        "type": "integer",
                        "description": "The number of lines",
                    },
                },
                "required": ["lines"],
            },
        }
