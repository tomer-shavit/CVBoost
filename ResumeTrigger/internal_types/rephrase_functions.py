from typing import List, TypedDict


class Line(TypedDict):
    type: str
    description: str


class InnerItemsProperties(TypedDict):
    old_line: Line
    new_line: Line


class NumOfLinesItemProperties(TypedDict):
    type: str
    description: str


class LineItemProperties(TypedDict):
    type: str
    properties: InnerItemsProperties
    required: List[str]


class LineItem(TypedDict):
    type: str
    items: LineItemProperties


class ParametersProperties(TypedDict):
    lines: LineItem
    number_of_lines: NumOfLinesItemProperties


class RephraseParameters(TypedDict):
    type: str
    properties: ParametersProperties
    required: List[str]


class RephraseFunction(TypedDict):
    name: str
    parameters: RephraseParameters
