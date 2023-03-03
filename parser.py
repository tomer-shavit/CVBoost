from typing import List, Optional, Dict, Any
import PyPDF2
import re


class Parser:
    def __init__(self, pdf_path: str):
        self._pdf_path = pdf_path
        self._resume_text = ""
        self._resume_lines_list = []
        self._resume_paragraphs_list = []
        self._current_line_index = 0
        self.extract_text_from_pdf()

    def get_current_line(self) -> Optional[str]:
        if self._current_line_index < len(self._resume_lines_list):
            current_line = self._resume_lines_list[self._current_line_index]
            self._current_line_index += 1
            return current_line

        return None

    def add_lines_from_page(self, page: str) -> None:
        lines_list: List[str] = page.split("\n")
        current_line: str
        for line in lines_list:
            current_line = re.sub(' +', ' ', line.strip())
            if len(current_line ) != 0:
                self._resume_lines_list.append(current_line)

    def extract_text_from_pdf(self) -> None:
        pdf_reader = PyPDF2.PdfReader(open(self._pdf_path, 'rb'))

        page_content: str
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_content = page.extract_text()
            self._resume_text += page_content
            self.add_lines_from_page(page_content)
            self.add_paragraphs_from_page(page_content)

    def add_paragraphs_from_page(self, page: str) -> None:
        paragraphs_list: List[str] = page.split("\n\n")
        current_line: str
        for line in paragraphs_list:
            current_line = re.sub(' +', ' ', line.strip())
            self._resume_paragraphs_list.append(current_line)


    def get_resume_lines_list(self) -> List[str]:
        return self._resume_lines_list


    def get_resume_paragraphs_list(self) -> List[str]:
        return self._resume_paragraphs_list
