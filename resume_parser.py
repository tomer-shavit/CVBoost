from typing import List, Optional, Dict, Any
from resume_line import ResumeLine
# import PyPDF2
import re
import fitz


class ResumeParser:
    def __init__(self, pdf_path: str):
        self._pdf_path: str = pdf_path
        self._resume_text: str = ""
        self._resume_lines_list: List[ResumeLine] = []
        self._current_line_index = 0
        self.extract_text_from_pdf()
        # for line in self._resume_lines_list:
        #     print(line)


    def get_current_line(self) -> Optional[ResumeLine]:
        if self._current_line_index < len(self._resume_lines_list):
            current_line = self._resume_lines_list[self._current_line_index]
            self._current_line_index += 1
            return current_line

        return None

    def extract_text_from_pdf(self) -> None:
        doc = fitz.open(self._pdf_path)  # open document
        for page in doc:  # iterate the document pages
            page_content_blocks = page.get_text("blocks", sort=True)
            self._resume_text += page.get_text()
            for block in page_content_blocks:
                # block indexes according to the docs
                block_text = re.sub("\n|\n\s*| \s*", " ", block[4]).strip()
                if len(block_text) != 0:
                    self._resume_lines_list.append(ResumeLine(block_text, block[0], block[2], block[1], block[3]))

    def get_resume_lines_list(self) -> List[ResumeLine]:
        return self._resume_lines_list

    @property
    def resume_text(self) ->str:
        return self._resume_text
