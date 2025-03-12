import logging
import langdetect  # type: ignore
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Optional

from .booster import Booster
from .file_check import is_valid_resume, detect_language_from_content, PDFValidationError
from .resume_parser import ResumeParser
from .test_result import FileTestResult


def boost_resume_to_json(pdf_bytes: bytes, user_id: str, explicit_language: Optional[str] = None) -> Tuple[bool, int, str, str]:
    try:
        # First, detect the language from the content
        detected_language = detect_language_from_content(pdf_bytes)
        
        # Use explicit language if provided, otherwise use detected language
        language = explicit_language if explicit_language else detected_language
        
        # Validate the resume
        test_result: FileTestResult = is_valid_resume(pdf_bytes, language)
        if not test_result.is_passed():
            logging.error(f"Resume validation failed: {test_result.error_message}")
            return test_result.status, 400, test_result.error_message, "en"  # Error messages in English
    
        parser: ResumeParser = ResumeParser(pdf_bytes)
    
        # Pass language parameter to Booster
        booster = Booster(user_id, parser.resume_text, language=language)
    
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(booster.feedback_resume, 0),
                executor.submit(booster.rephrase_lines),
            ]
    
            for future in as_completed(futures):  # type: ignore
                if future.exception():
                    raise future.exception()  # type: ignore
    
        return True, 200, booster.make_json(), language
        
    except PDFValidationError as e:
        # Handle validation errors
        logging.error(f"PDF validation error: {str(e)}")
        return False, 400, str(e), "en"
        
    except Exception as e:
        # Handle other errors
        logging.error(f"An error occurred while processing the resume: {e}")
        
        # Error message always in English
        error_message = "Oops! something went wrong on our side, please check again later."
        
        return (
            False,
            500,
            error_message,
            "en",  # Error messages in English
        )
