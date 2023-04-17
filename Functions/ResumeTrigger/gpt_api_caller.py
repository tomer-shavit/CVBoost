import os
import openai
from typing import Dict, List
from .gpt_api_response import GptApiResponse

class GptApiCaller:
    MODEL_TYPE = "gpt-3.5-turbo"

    def __init__(self):
        self._model = openai
        self._tokens_used: int = 0
        self._model.api_key = os.getenv("GPT_API_KEY1")

    def call_api(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> GptApiResponse:
        try:
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model=self.MODEL_TYPE,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return GptApiResponse(response['id'], response["usage"], response["choices"])

        except Exception as e:
            print("Unexpected error: %s" % str(e))

    @staticmethod
    def create_message(role: str, content: str) -> Dict[str, str]:
        return {"role": role, "content": content}

    def add_tokens(self, amount: int) -> int:
        self._tokens_used += amount
        return self._tokens_used

    @property
    def tokens_used(self) -> int:
        return self._tokens_used
