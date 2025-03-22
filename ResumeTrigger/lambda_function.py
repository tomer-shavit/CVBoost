import json
import logging
import base64
import traceback
from .main import boost_resume_to_json
from .file_check import PDFValidationError

def parse_multipart_body(body_bytes, boundary):
    """
    Parse multipart/form-data body into parts
    Returns a list of tuples (name, content, filename)
    """
    parts = []
    # Split by boundary
    raw_parts = body_bytes.split(f'--{boundary}'.encode('utf-8'))
    
    # Process each part
    for part in raw_parts:
        if b'Content-Disposition: form-data;' in part:
            # Extract name
            name_match = part.split(b'name="')[1].split(b'"')[0] if b'name="' in part else None
            
            # Extract filename if present
            filename = None
            if b'filename="' in part:
                filename = part.split(b'filename="')[1].split(b'"')[0]
                
            # Extract content
            content_start = part.find(b'\r\n\r\n') + 4 if b'\r\n\r\n' in part else 0
            content = part[content_start:].strip() if content_start > 0 else None
            
            if name_match and content:
                parts.append((name_match.decode('utf-8'), content, filename))
                
    return parts

def parse_multipart_data(event):
    """
    Parse multipart/form-data from API Gateway event
    Returns file_content, user_id, and explicit_language
    """
    try:
        # Try to parse as JSON first
        if event.get('isBase64Encoded', False):
            body_str = base64.b64decode(event['body']).decode('utf-8')
            body = json.loads(body_str)
        else:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract file content and user ID
        file_content = base64.b64decode(body['resume'])
        user_id = body['userId']
        explicit_language = body.get('language')
        return file_content, user_id, explicit_language
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logging.warning(f"JSON parsing failed: {str(e)}. Trying multipart/form-data.")
        
        # If JSON parsing fails, try to handle as multipart/form-data
        try:
            # This is a simplified approach - in production, use a proper multipart parser
            if event.get('isBase64Encoded', False):
                body_bytes = base64.b64decode(event['body'])
            else:
                body_bytes = event['body'].encode('utf-8') if isinstance(event['body'], str) else event['body']
            
            # Extract boundary from content-type header
            content_type = event.get('headers', {}).get('content-type', '')
            if not content_type.startswith('multipart/form-data'):
                raise ValueError(f"Expected multipart/form-data content type, got: {content_type}")
            
            boundary = content_type.split('boundary=')[1].strip()
            
            # Parse multipart form data
            parts = parse_multipart_body(body_bytes, boundary)
            
            file_content = None
            user_id = 'unknown'
            explicit_language = None
            
            for name, content, filename in parts:
                if name == 'resume':
                    file_content = content
                elif name == 'userId':
                    user_id = content.decode('utf-8')
                elif name == 'language':
                    explicit_language = content.decode('utf-8')
            
            if not file_content:
                raise ValueError("No resume file found in the request")
                
            return file_content, user_id, explicit_language
            
        except Exception as e:
            logging.error(f"Failed to parse multipart/form-data: {str(e)}")
            raise
    
    except Exception as e:
        logging.error(f"Failed to parse request: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    AWS Lambda handler function for the ResumeTrigger
    """
    logging.info('Python Lambda function processed a request.')
    
    try:
        # Check if the request is from API Gateway
        if 'body' in event:
            # Handle API Gateway request
            try:
                # Try to parse as JSON first
                if event.get('isBase64Encoded', False):
                    body_str = base64.b64decode(event['body']).decode('utf-8')
                    body = json.loads(body_str)
                else:
                    body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                
                # Extract file content and user ID
                file_content = base64.b64decode(body['resume'])
                user_id = body['userId']
                explicit_language = body.get('language')
                
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logging.warning(f"JSON parsing failed: {str(e)}. Trying multipart/form-data.")
                
                # If JSON parsing fails, try to handle as multipart/form-data
                try:
                    # This is a simplified approach - in production, use a proper multipart parser
                    if event.get('isBase64Encoded', False):
                        body_bytes = base64.b64decode(event['body'])
                    else:
                        body_bytes = event['body'].encode('utf-8') if isinstance(event['body'], str) else event['body']
                    
                    # Extract boundary from content-type header
                    content_type = event.get('headers', {}).get('content-type', '')
                    if not content_type.startswith('multipart/form-data'):
                        raise ValueError(f"Expected multipart/form-data content type, got: {content_type}")
                    
                    boundary = content_type.split('boundary=')[1].strip()
                    
                    # Parse multipart form data (simplified)
                    parts = body_bytes.split(f'--{boundary}'.encode('utf-8'))
                    
                    file_content = None
                    user_id = None
                    explicit_language = None
                    
                    for part in parts:
                        if b'name="resume"' in part:
                            # Extract file content
                            file_start = part.find(b'\r\n\r\n') + 4
                            file_content = part[file_start:].strip()
                        elif b'name="userId"' in part:
                            # Extract user ID
                            id_start = part.find(b'\r\n\r\n') + 4
                            user_id = part[id_start:].strip().decode('utf-8')
                        elif b'name="language"' in part:
                            # Extract language
                            lang_start = part.find(b'\r\n\r\n') + 4
                            explicit_language = part[lang_start:].strip().decode('utf-8')
                    
                    if not file_content:
                        raise ValueError("Missing 'resume' field in form data")
                    if not user_id:
                        raise ValueError("Missing 'userId' field in form data")
                        
                except Exception as form_error:
                    logging.error(f"Error parsing multipart/form-data: {str(form_error)}")
                    return {
                        'statusCode': 400,
                        'headers': {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Language",
                            "Content-Language": "en"
                        },
                        'body': json.dumps({"error": f"Invalid request format: {str(form_error)}"})
                    }
        else:
            # Handle direct invocation
            if 'resume' not in event:
                raise ValueError("Missing 'resume' field in direct invocation")
            if 'userId' not in event:
                raise ValueError("Missing 'userId' field in direct invocation")
                
            file_content = base64.b64decode(event['resume'])
            user_id = event['userId']
            explicit_language = event.get('language')
            
        logging.info(f'Received resume file for user: {user_id}')
        
        # Pass file content to boost function - language will be detected from content
        boost_passed, request_status, boosted_response, detected_language = boost_resume_to_json(
            file_content, user_id, explicit_language)
        
        # Set CORS headers with detected language
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Language",
            "Content-Language": detected_language
        }
        
        if not boost_passed:
            return {
                'statusCode': request_status,
                'headers': headers,
                'body': json.dumps({"error": boosted_response}) if request_status == 400 else boosted_response
            }
        else:
            return {
                'statusCode': request_status,
                'headers': headers,
                'body': boosted_response,
                'isBase64Encoded': False
            }
            
    except PDFValidationError as e:
        # Handle PDF validation errors specifically
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
        # Log the full stack trace for debugging
        logging.error(f"Error processing request: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Error messages always in English
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