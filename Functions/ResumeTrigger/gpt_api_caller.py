import os
from openai import OpenAI
from typing import Dict, List, Optional, Any
from .gpt_api_response import GptApiResponse


class GptApiCaller:
    GPT4O = "gpt-4o"

    def __init__(self):
        self._tokens_used: int = 0
        self._client = OpenAI(api_key=os.getenv("GPT_API_KEY1"))

    def call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        model_type: str = GPT4O,
        functions=None,
    ) -> Optional[GptApiResponse]:
        try:
            # Handle the case where functions is provided (legacy function calling)
            if functions:
                # Convert legacy functions to tools format
                tools = [{
                    "type": "function",
                    "function": functions[0]
                }]
                
                response = self._client.chat.completions.create(
                    model=model_type,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools,
                    tool_choice={"type": "function", "function": {"name": functions[0]["name"]}}
                )
                
                # Convert the response to a dictionary for compatibility with GptApiResponse
                response_dict = {
                    "id": response.id,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "choices": [{
                        "message": {
                            "function_call": {
                                "arguments": response.choices[0].message.tool_calls[0].function.arguments
                            }
                        }
                    }]
                }
                
                return GptApiResponse(
                    response_dict["id"], response_dict["usage"], response_dict["choices"]
                )
            else:
                # Standard chat completion without functions
                response = self._client.chat.completions.create(
                    model=model_type,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Convert the response to a dictionary for compatibility with GptApiResponse
                response_dict = {
                    "id": response.id,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "choices": [{
                        "message": {
                            "content": response.choices[0].message.content
                        }
                    }]
                }
                
                return GptApiResponse(
                    response_dict["id"], response_dict["usage"], response_dict["choices"]
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
