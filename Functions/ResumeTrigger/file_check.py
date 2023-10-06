import fitz
import langdetect
from .test_result import FileTestResult

# # Defining a function that checks if the content is a PDF (bytes)
# def is_pdf(content: bytes) -> bool:
#     # Check if the content starts with the PDF file header (PDF signature)
#     return content.startswith(b'%PDF-')

# Defining a function that checks if the PDF has at most 2 pages
def has_max_2_pages(content: bytes) -> bool:
    pdf_file = fitz.open(stream=content, filetype="pdf")
    num_pages = pdf_file.page_count
    pdf_file.close()
    return num_pages <= 2

# Defining a function that checks if the PDF is in English
def is_english(content: bytes) -> bool:
    pdf_file = fitz.open(stream=content, filetype="pdf")
    text = ""
    for i in range(pdf_file.page_count):
        page = pdf_file.load_page(i)
        page_text = page.get_text()
        text += page_text
    pdf_file.close()
    language = langdetect.detect(text)
    return language == "en"

# Defining a function that checks if the resume is valid
def is_valid_resume(content: bytes) -> FileTestResult:
    if not has_max_2_pages(content):
        return FileTestResult(False, FileTestResult.LENGTH, "The resume has more than 2 pages.")
    if not is_english(content):
        return FileTestResult(False, FileTestResult.LANG, "The resume is not in English.")
    return FileTestResult(True, FileTestResult.DEFAULT, "")
