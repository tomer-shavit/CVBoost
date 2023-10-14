from enum import IntEnum

class BoostVersion(IntEnum):
    V1 = 1

class FEEDBACK_TYPE(IntEnum):
    REPHRASE = 1
    CLARITY = 2
    RELEVANCE = 3
    ACHIEVEMENTS = 4
    KEYWORDS = 5
    SUMMARY = 6
    LINE = 7