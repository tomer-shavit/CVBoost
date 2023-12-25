from typing import TypedDict


class DescriptionField(TypedDict):
    type: str
    description: str


class FeedbackProperties(TypedDict):
    feedback: DescriptionField
    score: DescriptionField


class FeedbackCategory(TypedDict):
    type: str
    properties: FeedbackProperties


class BoostParametersProperties(TypedDict):
    clarity: FeedbackCategory
    relevance: FeedbackCategory
    achievements: FeedbackCategory
    keywords: FeedbackCategory


class BoostParameters(TypedDict):
    type: str
    properties: BoostParametersProperties


class FeedbackFunction(TypedDict):
    name: str
    parameters: BoostParameters
