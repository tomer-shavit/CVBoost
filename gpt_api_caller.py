import os, openai

class GptApiCaller:
    MODEL_TYPE = "text-davinci-003"
    def __init__(self):
        self._model = openai
        self._model.api_key = os.getenv("GPT_API_KEY1")

    def call_api(self, prompt:str, temperature:float, max_tokens:int):
        try:
            # Call the OpenAI API
            response = openai.Completion.create(
                engine=self.MODEL_TYPE,
                prompt=prompt,
                max_tokens=max_tokens
            )
            # Extract the generated text from the response
            text = response.choices[0].text
            return text
        except Exception as e:
            print("Unexpected error: %s" % str(e))
