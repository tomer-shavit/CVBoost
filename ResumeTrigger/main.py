import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Optional

from .booster import Booster
from .file_check import is_valid_resume, detect_language_from_content, PDFValidationError
from .resume_parser import ResumeParser
from .test_result import FileTestResult
from .cloudwatch_logger import get_logger

# Replace standard logger with CloudWatch logger
logger = get_logger("main")

def boost_resume_to_json(pdf_bytes: bytes, user_id: str) -> Tuple[bool, int, str, str]:
    # Use user-specific logger for better traceability
    user_logger = get_logger("main", user_id)
    
    try:
        # Detect the language from the content
        detected_language = detect_language_from_content(pdf_bytes)
        user_logger.info(f"Detected language: {detected_language}")
        
        # Validate the resume
        test_result: FileTestResult = is_valid_resume(pdf_bytes, detected_language)
        if not test_result.is_passed():
            user_logger.error(f"Resume validation failed: {test_result.error_message}")
            return test_result.status, 400, test_result.error_message, "en"  # Error messages in English
    
        # Parse resume and create booster
        parser: ResumeParser = ResumeParser(pdf_bytes)
        booster = Booster(user_id, parser.resume_text, language=detected_language)
    
        # Process resume with concurrent tasks
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(booster.feedback_resume, 0),
                executor.submit(booster.rephrase_lines),
            ]
    
            for future in as_completed(futures):  # type: ignore
                if future.exception():
                    exception = future.exception()  # type: ignore
                    user_logger.error(f"Error in concurrent processing: {str(exception)}")
                    # Re-raise the original exception
                    if exception:
                        raise exception
    
        user_logger.info("Resume processing completed successfully")
        return True, 200, booster.make_json(), detected_language
        
    except PDFValidationError as e:
        # Handle validation errors
        user_logger.error(f"PDF validation error: {str(e)}")
        return False, 400, str(e), "en"
        
    except Exception as e:
        # Handle other errors
        user_logger.error(f"Error processing resume: {str(e)}", exc_info=True)
        
        # Error message always in English
        error_message = "Oops! something went wrong on our side, please check again later."
        
        return (
            False,
            500,
            error_message,
            "en",  # Error messages in English
        )
