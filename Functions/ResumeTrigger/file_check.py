import fitz
import langdetect
from .test_result import FileTestResult

# Defining a function that checks if the file is a pdf


def is_pdf(file: str) -> bool:
    extension = file.split(".")[-1]
    return extension == "pdf"


# Defining a function that checks if the pdf has at most 2 pages
def has_max_2_pages(file: str) -> bool:
    pdf_file = fitz.open(file)
    num_pages = pdf_file.page_count
    pdf_file.close()
    return num_pages <= 2


# Defining a function that checks if the pdf is in English
def is_english(file: str) -> bool:
    pdf_file = fitz.open(file)
    text = ""
    for i in range(pdf_file.page_count):
        page = pdf_file.load_page(i)
        page_text = page.get_text()
        text += page_text
    pdf_file.close()
    language = langdetect.detect(text)
    return language == "en"


# Defining a function that checks if the resume is valid
def is_valid_resume(file: str) -> FileTestResult:
    # if not is_pdf(file):
    #     return FileTestResult(False, FileTestResult.TYPE, "The file is not a pdf.")
    if not has_max_2_pages(file):
        return FileTestResult(False, FileTestResult.LENGTH, "The resume has more than 2 pages.")
    if not is_english(file):
        return FileTestResult(False, FileTestResult.LANG, "The resume is not in English.")
    return FileTestResult(True, FileTestResult.DEFAULT, "")
