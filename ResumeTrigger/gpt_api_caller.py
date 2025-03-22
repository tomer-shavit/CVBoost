import os
import openai
from typing import Dict, List, Optional, Any
from ResumeTrigger.gpt_api_response import GptApiResponse


class GptApiCaller:
    GPT4O = "gpt-4o"

    def __init__(self):
        self._tokens_used: int = 0
        self._client = openai.Client(api_key=os.getenv("GPT_API_KEY1"))

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
                
                # Safely extract usage information
                usage_dict = self._extract_usage(response.usage)
                
                # Convert the response to a dictionary for compatibility with GptApiResponse
                response_dict = {
                    "id": response.id,
                    "usage": usage_dict,
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
                
                # Safely extract usage information
                usage_dict = self._extract_usage(response.usage)
                
                # Convert the response to a dictionary for compatibility with GptApiResponse
                response_dict = {
                    "id": response.id,
                    "usage": usage_dict,
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
    
    def _extract_usage(self, usage_data):
        """
        Safely extract usage information from response, handling both object and dict formats
        """
        usage_dict = {}
        
        # Handle the case where usage_data is already a dictionary
        if isinstance(usage_data, dict):
            usage_dict = usage_data
        else:
            # Try to extract attributes from an object
            try:
                usage_dict["prompt_tokens"] = usage_data.prompt_tokens
                usage_dict["completion_tokens"] = usage_data.completion_tokens
                usage_dict["total_tokens"] = usage_data.total_tokens
            except AttributeError:
                # If we can't get all the attributes, set default values
                if not "prompt_tokens" in usage_dict:
                    usage_dict["prompt_tokens"] = 0
                if not "completion_tokens" in usage_dict:
                    usage_dict["completion_tokens"] = 0
                if not "total_tokens" in usage_dict:
                    usage_dict["total_tokens"] = 0
        
        return usage_dict
        
    def create_message(self, role: str, content: str) -> Dict[str, str]:
        return {"role": role, "content": content}

    def add_tokens(self, tokens: int) -> None:
        self._tokens_used += tokens

    @property
    def tokens_used(self) -> int:
        return self._tokens_used
