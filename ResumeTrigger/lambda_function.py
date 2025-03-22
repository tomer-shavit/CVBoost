import json
import logging
import base64
import traceback
from .main import boost_resume_to_json
from .file_check import PDFValidationError

def parse_multipart_body(body_bytes, boundary):
    """
    Parse multipart/form-data body into parts.
    Returns a list of tuples (name, content, filename).
    """
    parts = []
    raw_parts = body_bytes.split(f'--{boundary}'.encode('utf-8'))
    for part in raw_parts:
        if b'Content-Disposition: form-data;' in part:
            try:
                name = part.split(b'name="')[1].split(b'"')[0]
            except IndexError:
                name = None
            filename = None
            if b'filename="' in part:
                try:
                    filename = part.split(b'filename="')[1].split(b'"')[0]
                except IndexError:
                    filename = None
            content_start = part.find(b'\r\n\r\n') + 4 if b'\r\n\r\n' in part else 0
            content = part[content_start:].strip() if content_start > 0 else None
            if name and content:
                parts.append((name.decode('utf-8'), content, filename))
    return parts

def parse_multipart_data(event):
    """
    Parse data from an API Gateway event.
    Handles both JSON and multipart/form-data.
    Returns file_content, user_id, and explicit_language.
    """
    headers = event.get('headers', {})
    # Use either lowercase or title-case header name
    content_type = headers.get('content-type') or headers.get('Content-Type', '')
    
    if content_type.startswith('multipart/form-data'):
        # Process multipart/form-data without decoding binary PDF data
        if event.get('isBase64Encoded', False):
            body_bytes = base64.b64decode(event['body'])
        else:
            body_bytes = event['body'] if isinstance(event['body'], bytes) else event['body'].encode('utf-8')
        try:
            boundary = content_type.split('boundary=')[1].strip()
        except IndexError:
            raise ValueError("Boundary not found in Content-Type header.")
        parts = parse_multipart_body(body_bytes, boundary)
        file_content = None
        user_id = 'unknown'
        explicit_language = None
        for name, content, _ in parts:
            if name == 'resume':
                file_content = content
            elif name == 'userId':
                user_id = content.decode('utf-8')
            elif name == 'language':
                explicit_language = content.decode('utf-8')
        if not file_content:
            raise ValueError("No resume file found in the request")
        return file_content, user_id, explicit_language
    else:
        # Assume JSON input
        if event.get('isBase64Encoded', False):
            body_str = base64.b64decode(event['body']).decode('utf-8')
        else:
            body_str = event['body'] if isinstance(event['body'], str) else event['body']
        body = json.loads(body_str)
        file_content = base64.b64decode(body['resume'])
        user_id = body['userId']
        explicit_language = body.get('language')
        return file_content, user_id, explicit_language

def lambda_handler(event, context):
    """
    AWS Lambda handler function for the ResumeTrigger.
    """
    logging.info('Python Lambda function processed a request.')
    try:
        if 'body' in event:
            headers = event.get('headers', {})
            content_type = headers.get('content-type') or headers.get('Content-Type', '')
            if content_type.startswith('multipart/form-data'):
                file_content, user_id, explicit_language = parse_multipart_data(event)
            else:
                # Assume JSON input
                if event.get('isBase64Encoded', False):
                    body_str = base64.b64decode(event['body']).decode('utf-8')
                else:
                    body_str = event['body'] if isinstance(event['body'], str) else event['body']
                body = json.loads(body_str)
                file_content = base64.b64decode(body['resume'])
                user_id = body['userId']
                explicit_language = body.get('language')
        else:
            # Direct invocation
            if 'resume' not in event or 'userId' not in event:
                raise ValueError("Missing 'resume' or 'userId' field in direct invocation")
            file_content = base64.b64decode(event['resume'])
            user_id = event['userId']
            explicit_language = event.get('language')
        
        logging.info(f"Received resume file for user: {user_id}")
        boost_passed, request_status, boosted_response, detected_language = boost_resume_to_json(
            file_content, user_id, explicit_language
        )
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Language",
            "Content-Language": detected_language
        }
        response = {
            'statusCode': request_status,
            'headers': headers,
            'body': boosted_response,
            'isBase64Encoded': False
        }
        if not boost_passed and request_status == 400:
            response['body'] = json.dumps({"error": boosted_response})
        return response
        
    except PDFValidationError as e:
        logging.error(f"PDF validation error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Language",
                "Content-Language": "en"
            },
            'body': json.dumps({"error": str(e)})
        }
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        logging.error(traceback.format_exc())
        error_message = "Please upload a valid PDF resume file."
        return {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Language",
                "Content-Language": "en"
            },
            'body': json.dumps({"error": error_message})
        }
