from typing import Dict, List, Any
class GptApiResponse:
    def __init__(self,id:str,  usage: Dict[str,int], choices: List[Dict[str, Any]]):
        self._id = id
        self._usage: Dict[str, int] = usage
        self._choices: List[Dict[str, Any]] = choices

    @property
    def id(self) -> str:
        return self._id

    @property
    def usage(self) -> Dict[str, int]:
        return self._usage

    @property
    def choices(self) -> List[Dict[str, Any]]:
        return self._choices
