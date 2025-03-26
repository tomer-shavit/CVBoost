import json
import logging
from logging import Logger
import base64
import traceback
from .main import boost_resume_to_json
from .file_check import PDFValidationError
from .cloudwatch_logger import get_logger

# Initialize a basic logger first as a fallback
logging.basicConfig(level=logging.INFO)
# Then try to get the CloudWatch logger
_logger: Logger | None = None

def get_lambda_logger():
    """Get a logger instance, with error handling to avoid circular imports"""
    global _logger
    if _logger is None:
        try:
            _logger = get_logger("lambda_function")
        except Exception as e:
            # Fall back to standard logger if CloudWatch logger fails
            _logger = logging.getLogger("lambda_function")
            _logger.setLevel(logging.INFO)
            _logger.error(f"Failed to initialize CloudWatch logger: {str(e)}")
    return _logger

# Get the logger instance
logger = get_lambda_logger()

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
    Returns file_content, user_id.
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
        for name, content, _ in parts:
            if name == 'resume':
                file_content = content
            elif name == 'userId':
                user_id = content.decode('utf-8')
        if not file_content:
            raise ValueError("No resume file found in the request")
        return file_content, user_id
    else:
        # Assume JSON input
        if event.get('isBase64Encoded', False):
            body_str = base64.b64decode(event['body']).decode('utf-8')
        else:
            body_str = event['body'] if isinstance(event['body'], str) else json.dumps(event['body'])
        
        try:
            body = json.loads(body_str)
            logger.info("Successfully parsed JSON body")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise
            
        file_content = base64.b64decode(body['resume'])
        user_id = body['userId']
        return file_content, user_id

def lambda_handler(event, context):
    """
    AWS Lambda handler function for the ResumeTrigger.
    """
    global logger
    request_id = context.aws_request_id if context else 'local'
    logger.info(f'Lambda invoked with request ID: {request_id}')
    
    try:
        if 'body' in event:
            headers = event.get('headers', {})
            content_type = headers.get('content-type') or headers.get('Content-Type', '')
            
            try:
                if content_type.startswith('multipart/form-data'):
                    file_content, user_id = parse_multipart_data(event)
                else:
                    # Assume JSON input
                    if isinstance(event['body'], dict):
                        body = event['body']
                    else:
                        if event.get('isBase64Encoded', False):
                            body_str = base64.b64decode(event['body']).decode('utf-8')
                        else:
                            body_str = event['body']
                        
                        try:
                            body = json.loads(body_str)
                        except json.JSONDecodeError as e:
                            error_msg = f"JSON decode error: {str(e)}"
                            logger.error(error_msg)
                            raise
                
                file_content = base64.b64decode(body['resume'])
                user_id = body['userId']
                
                # Update logger with user_id for traceability
                logger = get_logger("lambda_function", user_id)
                logger.info(f"Processing resume for user: {user_id}")
            except Exception as e:
                logger.error(f"Error parsing request body: {str(e)}")
                logger.error(traceback.format_exc())
                raise
        else:
            # Direct invocation
            if 'resume' not in event or 'userId' not in event:
                error_msg = "Missing 'resume' or 'userId' field in direct invocation"
                logger.error(error_msg)
                raise ValueError(error_msg)
            file_content = base64.b64decode(event['resume'])
            user_id = event['userId']
            
            # Update logger with user_id for traceability
            logger = get_logger("lambda_function", user_id)
            logger.info(f"Processing resume for user: {user_id}")
        
        # Process the resume
        boost_passed, request_status, boosted_response, detected_language = boost_resume_to_json(
            file_content, user_id
        )
        
        logger.info(f"Resume processing completed with status: {request_status}")
        
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
            error_msg = {"error": boosted_response}
            logger.error(f"Resume processing failed with error: {boosted_response}")
            response['body'] = json.dumps(error_msg)
        
        return response
        
    except PDFValidationError as e:
        error_msg = f"PDF validation error: {str(e)}"
        logger.error(error_msg)
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
        error_msg = f"Error processing request: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
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
