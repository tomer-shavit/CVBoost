import os
import sys
import json

# Add the Functions directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Now import directly
from ResumeTrigger.gpt_api_caller import GptApiCaller
from ResumeTrigger.prompt_factory import PromptFactory


def test_gpt_api_caller():
    # Initialize the GptApiCaller
    api_caller = GptApiCaller()
    
    # Create a simple test message
    messages = [
        api_caller.create_message("system", "You are a helpful assistant."),
        api_caller.create_message("user", "Hello, can you tell me about GPT-4o?")
    ]
    
    # Test standard chat completion with GPT-4o
    print("Testing standard chat completion with GPT-4o...")
    response = api_caller.call_api(
        messages=messages,
        temperature=0.7,
        max_tokens=100,
        # Using default model_type which is now GPT4O
        functions=None
    )
    
    if response:
        print("Response received successfully!")
        print(f"ID: {response.id}")
        print(f"Usage: {response.usage}")
        print(f"Content: {response.get_response_content(has_function=False)}")
    else:
        print("Failed to get a response.")
    
    # Test function calling with GPT-4o (English)
    print("\nTesting function calling with GPT-4o (English)...")
    # Create English prompt factory
    en_prompt_factory = PromptFactory(language='en')
    function_def = en_prompt_factory.build_feedback_function()
    
    function_messages = [
        api_caller.create_message("system", "You are a helpful resume assistant."),
        api_caller.create_message("user", "Please give me feedback on my resume.")
    ]
    
    response_with_function = api_caller.call_api(
        messages=function_messages,
        temperature=0,
        max_tokens=1000,
        # Using default model_type which is now GPT4O
        functions=[function_def]
    )
    
    if response_with_function:
        print("English function calling response received successfully!")
        print(f"ID: {response_with_function.id}")
        print(f"Usage: {response_with_function.usage}")
        function_args = response_with_function.get_response_content(has_function=True)
        print(f"Function arguments: {function_args}")
        
        try:
            parsed_args = json.loads(function_args)
            print(f"English feedback summary: {parsed_args.get('general_feedback', 'No feedback provided')[:100]}...")
            print(f"Keys in response: {list(parsed_args.keys())}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Raw function arguments:")
            print(function_args)
    else:
        print("Failed to get an English function calling response.")
    
    # Test function calling with GPT-4o (French)
    print("\nTesting function calling with GPT-4o (French)...")
    # Create French prompt factory
    fr_prompt_factory = PromptFactory(language='fr')
    function_def_fr = fr_prompt_factory.build_feedback_function()
    
    function_messages_fr = [
        api_caller.create_message("system", "Vous êtes un assistant de CV utile."),
        api_caller.create_message("user", "Veuillez me donner des commentaires sur mon CV.")
    ]
    
    response_with_function_fr = api_caller.call_api(
        messages=function_messages_fr,
        temperature=0,
        max_tokens=1000,
        # Using default model_type which is now GPT4O
        functions=[function_def_fr]
    )
    
    if response_with_function_fr:
        print("French function calling response received successfully!")
        print(f"ID: {response_with_function_fr.id}")
        print(f"Usage: {response_with_function_fr.usage}")
        function_args_fr = response_with_function_fr.get_response_content(has_function=True)
        print(f"Function arguments: {function_args_fr}")
        
        try:
            parsed_args_fr = json.loads(function_args_fr)
            print(f"French feedback summary: {parsed_args_fr.get('general_feedback', 'Aucun résumé fourni')[:100]}...")
            print(f"Keys in response: {list(parsed_args_fr.keys())}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Raw function arguments:")
            print(function_args_fr)
    else:
        print("Failed to get a French function calling response.")

if __name__ == "__main__":
    test_gpt_api_caller() 