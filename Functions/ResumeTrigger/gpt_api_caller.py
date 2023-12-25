import os
import openai
from typing import Dict, List, Optional
from .gpt_api_response import GptApiResponse


class GptApiCaller:
    GPT4 = "gpt-4-1106-preview"
    GPT3 = "gpt-3.5-turbo-1106"

    def __init__(self):
        self._model = openai
        self._tokens_used: int = 0
        self._model.api_key = os.getenv("GPT_API_KEY1")

    def call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        model_type: str,
        functions=None,
    ) -> Optional[GptApiResponse]:
        try:
            response = openai.ChatCompletion.create(
                model=model_type,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                functions=functions,
                function_call={"name": functions[0]["name"]},
            )
            return GptApiResponse(
                response["id"], response["usage"], response["choices"]
            )

        except Exception as e:
            print("Unexpected error: %s" % str(e))

        return None

    @staticmethod
    def create_message(role: str, content: str) -> Dict[str, str]:
        return {"role": role, "content": content}

    def add_tokens(self, amount: int) -> int:
        self._tokens_used += amount
        return self._tokens_used

    @property
    def tokens_used(self) -> int:
        return self._tokens_used
