from typing import Dict, List, Any


class GptApiResponse:
    def __init__(self, idx: str, usage: Dict[str, int], choices: List[Dict[str, Any]]):
        self._id = idx
        self._usage: Dict[str, int] = usage
        self._choices: List[Dict[str, Any]] = choices

    def __str__(self):
        return f"id: {self._id}, usage: {self._usage}, choices: {self._choices}"

    def get_response_content(self, has_function=True) -> str:
        if has_function:
            return self.choices[0]["message"]["function_call"]["arguments"]
        else:
            return self.choices[0]["message"]["content"]

    @property
    def id(self) -> str:
        return self._id

    @property
    def usage(self) -> Dict[str, int]:
        return self._usage

    @property
    def choices(self) -> List[Dict[str, Any]]:
        return self._choices
