import base64
import json
import os
import sys
import logging
from ResumeTrigger import handle_request

# Configure logging to see debug output
logging.basicConfig(level=logging.INFO)

def test_lambda(pdf_file_path, user_id="test-user", language=None):
    """
    Test the Lambda function locally with a PDF file
    
    Args:
        pdf_file_path: Path to the PDF file
        user_id: User ID to pass to the Lambda function
        language: Optional language code
    """
    # Check if the API key is set
    if not os.environ.get("GPT_API_KEY1"):
        print("WARNING: GPT_API_KEY1 environment variable is not set or empty")
        print("The Lambda function might fail when calling OpenAI APIs")
    
    # Read the PDF file
    try:
        with open(pdf_file_path, "rb") as f:
            pdf_content = f.read()
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return
    
    # For direct invocation (Method 1): Just use the raw PDF bytes
    event = {
        "resume": pdf_content,
        "userId": user_id
    }
    
    # Add language if provided
    if language:
        event["language"] = language
    
    # Create an empty context
    context = {}
    
    print(f"Invoking Lambda function with file: {pdf_file_path}")
    print(f"User ID: {user_id}")
    print(f"Language: {language if language else 'auto-detect'}")
    print(f"PDF size: {len(pdf_content)} bytes")
    
    # Invoke the Lambda handler
    try:
        response = handle_request(event, context)
        
        # Print the response
        print("\nLambda Response:")
        print(f"Status Code: {response.get('statusCode')}")
        
        # Print headers
        print("\nHeaders:")
        for key, value in response.get("headers", {}).items():
            print(f"  {key}: {value}")
        
        # Print body
        print("\nBody:")
        body = response.get("body", "{}")
        
        # Try to pretty-print if it's JSON
        try:
            if isinstance(body, str):
                body_dict = json.loads(body)
                print(json.dumps(body_dict, indent=2))
            else:
                print(json.dumps(body, indent=2))
        except:
            # If it's not valid JSON, just print it
            print(body)
        
        return response
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_lambda_gateway_style(pdf_file_path, user_id="test-user", language=None):
    """
    Test the Lambda function using API Gateway style input
    """
    try:
        with open(pdf_file_path, "rb") as f:
            pdf_content = f.read()
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return
    
    # Create mock API Gateway event with base64 encoded body
    payload = {
        "resume": base64.b64encode(pdf_content).decode('ascii'),
        "userId": user_id
    }
    
    if language:
        payload["language"] = language
    
    event = {
        "body": json.dumps(payload),
        "isBase64Encoded": False,
        "headers": {
            "content-type": "application/json"
        }
    }
    
    context = {}
    
    print(f"Invoking Lambda function (API Gateway style) with file: {pdf_file_path}")
    print(f"User ID: {user_id}")
    print(f"Language: {language if language else 'auto-detect'}")
    
    try:
        response = handle_request(event, context)
        
        # Print the response
        print("\nLambda Response:")
        print(f"Status Code: {response.get('statusCode')}")
        
        # Print headers
        print("\nHeaders:")
        for key, value in response.get("headers", {}).items():
            print(f"  {key}: {value}")
        
        # Print body
        print("\nBody:")
        body = response.get("body", "{}")
        
        # Try to pretty-print if it's JSON
        try:
            if isinstance(body, str):
                body_dict = json.loads(body)
                print(json.dumps(body_dict, indent=2))
            else:
                print(json.dumps(body, indent=2))
        except:
            # If it's not valid JSON, just print it
            print(body)
        
        return response
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Check if PDF path was provided
    if len(sys.argv) < 2:
        print("Usage: python test_lambda_locally.py <path_to_pdf_file> [user_id] [language] [method]")
        print("  method: 1 = direct invocation (default), 2 = API Gateway style")
        sys.exit(1)
    
    # Get arguments
    pdf_path = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else "test-user"
    language = sys.argv[3] if len(sys.argv) > 3 else None
    method = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    
    # Run the test
    if method == 2:
        test_lambda_gateway_style(pdf_path, user_id, language)
    else:
        test_lambda(pdf_path, user_id, language) 