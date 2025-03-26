import fitz  # type: ignore
import langdetect  # type: ignore
from typing import Optional
from .test_result import FileTestResult
from .cloudwatch_logger import get_logger

# Set up logger
logger = get_logger("file_check")

class PDFValidationError(Exception):
    """Exception raised for errors in PDF validation."""
    pass

# Defining a function that checks if the content is a PDF (bytes)
def is_pdf(content: bytes) -> bool:
    if not content.startswith(b'%PDF-'):
        error_msg = "The content is not a valid PDF file."
        logger.error(error_msg)
        raise PDFValidationError(error_msg)
    return True

# Defining a function that checks if the PDF has at most 2 pages
def has_max_2_pages(content: bytes) -> bool:
    try:
        pdf_file = fitz.open(stream=content, filetype="pdf")
        num_pages = pdf_file.page_count
        pdf_file.close()
        if num_pages > 2:
            error_msg = f"The resume has {num_pages} pages, which exceeds the maximum of 2 pages."
            logger.error(error_msg)
            raise PDFValidationError(error_msg)
        return True
    except Exception as e:
        if isinstance(e, PDFValidationError):
            raise
        error_msg = f"Error processing PDF: {str(e)}"
        logger.error(error_msg)
        raise PDFValidationError(error_msg)

# Function to extract text from PDF
def extract_text_from_pdf(content: bytes) -> str:
    try:
        pdf_file = fitz.open(stream=content, filetype="pdf")
        text = ""
        for i in range(pdf_file.page_count):
            page = pdf_file.load_page(i)
            page_text = page.get_text()
            text += page_text
        pdf_file.close()
        
        text_length = len(text.strip())
        if text_length == 0:
            error_msg = "The PDF does not contain any extractable text."
            logger.error(error_msg)
            raise PDFValidationError(error_msg)
        
        return text
    except Exception as e:
        if isinstance(e, PDFValidationError):
            raise
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(error_msg)
        raise PDFValidationError(error_msg)

# Function to detect language from content
def detect_language_from_content(content: bytes) -> str:
    text = extract_text_from_pdf(content)
    
    try:
        # Set langdetect to be deterministic
        langdetect.DetectorFactory.seed = 0
        
        # Get a sample of the text (first 1000 characters) for more reliable detection
        sample_text = text[:1000]
        
        # Detect language with probability
        detected_langs = langdetect.detect_langs(sample_text)
        
        # If French is detected with high probability, use French
        for lang in detected_langs:
            if lang.lang == 'fr' and lang.prob > 0.8:
                return "fr"
        
        # Default to English for any other language or low confidence
        return "en"
    except langdetect.LangDetectException as e:
        error_msg = f"Error detecting language: {str(e)}"
        logger.error(error_msg)
        raise PDFValidationError(error_msg)

# Defining a function that checks if the PDF is in the supported language
def is_supported_language(content: bytes, language: str = 'fr') -> bool:
    # If no language preference is specified, accept any language
    if not language:
        return True
        
    text = extract_text_from_pdf(content)
    
    try:
        # Set langdetect to be deterministic
        langdetect.DetectorFactory.seed = 0
        
        detected_language = langdetect.detect(text)
        
        # For French, we accept 'fr' language code
        if language == 'fr' and detected_language != "fr":
            error_msg = f"The resume is not in French. Detected language: {detected_language}"
            logger.error(error_msg)
            raise PDFValidationError(error_msg)
        # For English, we accept 'en' language code
        elif language == 'en' and detected_language != "en":
            error_msg = f"The resume is not in English. Detected language: {detected_language}"
            logger.error(error_msg)
            raise PDFValidationError(error_msg)
        # Default to accepting any language if not specified
        return True
    except langdetect.LangDetectException as e:
        if language in ['fr', 'en']:
            error_msg = f"Error verifying language: {str(e)}"
            logger.error(error_msg)
            raise PDFValidationError(error_msg)
        # If language detection fails but no specific language is required, accept the document
        logger.warning(f"Language detection failed, but no specific language required: {str(e)}")
        return True

# Defining a function that checks if the resume is valid
def is_valid_resume(content: bytes, language: Optional[str] = None) -> FileTestResult:
    # Get language from environment if not provided
    if language is None:
        try:
            language = detect_language_from_content(content)
        except PDFValidationError as e:
            logger.error(f"Language detection failed: {str(e)}")
            return FileTestResult(False, FileTestResult.TYPE, str(e))
    
    try:
        # Run all validations, which will throw exceptions if they fail
        is_pdf(content)
        has_max_2_pages(content)
        is_supported_language(content, language)
        
        # If we get here, all validations passed
        return FileTestResult(True, FileTestResult.DEFAULT, "")
        
    except PDFValidationError as e:
        # Determine the error type based on the error message
        error_type = FileTestResult.TYPE
        if "pages" in str(e):
            error_type = FileTestResult.LENGTH
        elif "language" in str(e):
            error_type = FileTestResult.LANG
            
        logger.error(f"Resume validation failed: {str(e)}")
        return FileTestResult(False, error_type, str(e))
