import logging
import json
from .main import boost_resume_to_json

def handle_request(event, context):
    """
    AWS Lambda handler function for the ResumeTrigger
    """
    logging.info('Python Lambda function processed a request.')
    
    try:
        # Get the resume file from the request
        try:
            # For multipart/form-data requests
            if 'body' in event and event.get('isBase64Encoded', False):
                # This would need proper multipart parsing in production
                # Simplified for now - actual parsing is in lambda_function.py
                from lambda_function import parse_multipart_data
                file_content, user_id, explicit_language = parse_multipart_data(event)
            else:
                # Direct invocation with binary content
                file_content = event.get('resume', None)
                user_id = event.get('userId', 'unknown')
                explicit_language = event.get('language', None)
                
            if not file_content:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Please upload a pdf resume file.'})
                }
                
        except Exception as e:
            logging.error(str(e))
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Please upload a pdf resume file.'})
            }

        # Process the resume
        boost_passed, request_status, boosted_response, language = boost_resume_to_json(
            file_content, user_id, explicit_language)

        # Set CORS headers
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Content-Language": language
        }

        if not boost_passed:
            return {
                'statusCode': request_status,
                'headers': headers,
                'body': boosted_response
            }
        else:
            return {
                'statusCode': request_status,
                'headers': headers,
                'body': boosted_response
            }

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

# For backward compatibility with existing code
lambda_handler = handle_request 