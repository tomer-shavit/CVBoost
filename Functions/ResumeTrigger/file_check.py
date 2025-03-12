import fitz  # type: ignore
import langdetect  # type: ignore
import os
from typing import Optional
from .test_result import FileTestResult

class PDFValidationError(Exception):
    """Exception raised for errors in PDF validation."""
    pass

# Defining a function that checks if the content is a PDF (bytes)
def is_pdf(content: bytes) -> bool:
    if not content.startswith(b'%PDF-'):
        raise PDFValidationError("The content is not a valid PDF file.")
    return True

# Defining a function that checks if the PDF has at most 2 pages
def has_max_2_pages(content: bytes) -> bool:
    try:
        pdf_file = fitz.open(stream=content, filetype="pdf")
        num_pages = pdf_file.page_count
        pdf_file.close()
        if num_pages > 2:
            raise PDFValidationError(f"The resume has {num_pages} pages, which exceeds the maximum of 2 pages.")
        return True
    except Exception as e:
        if isinstance(e, PDFValidationError):
            raise
        raise PDFValidationError(f"Error processing PDF: {str(e)}")

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
        
        if not text.strip():
            raise PDFValidationError("The PDF does not contain any extractable text.")
        
        return text
    except Exception as e:
        if isinstance(e, PDFValidationError):
            raise
        raise PDFValidationError(f"Error extracting text from PDF: {str(e)}")

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
        raise PDFValidationError(f"Error detecting language: {str(e)}")

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
            raise PDFValidationError(f"The resume is not in French. Detected language: {detected_language}")
        # For English, we accept 'en' language code
        elif language == 'en' and detected_language != "en":
            raise PDFValidationError(f"The resume is not in English. Detected language: {detected_language}")
        # Default to accepting any language if not specified
        return True
    except langdetect.LangDetectException as e:
        if language in ['fr', 'en']:
            raise PDFValidationError(f"Error verifying language: {str(e)}")
        # If language detection fails but no specific language is required, accept the document
        return True

# Defining a function that checks if the resume is valid
def is_valid_resume(content: bytes, language: Optional[str] = None) -> FileTestResult:
    # Get language from environment if not provided
    if language is None:
        try:
            language = detect_language_from_content(content)
        except PDFValidationError as e:
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
            
        return FileTestResult(False, error_type, str(e))
