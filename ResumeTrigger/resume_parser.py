from typing import List, Optional
from .resume_line import ResumeLine
import re
import fitz  # type: ignore



class ResumeParser:
    def __init__(self, pdf_bytes: bytes):
        self._pdf_bytes: bytes = pdf_bytes
        self._resume_text: str = ""
        self._resume_lines_list: List[ResumeLine] = []
        self._current_line_index = 0
        self.extract_text_from_pdf()

    def get_current_line(self) -> Optional[ResumeLine]:
        if self._current_line_index < len(self._resume_lines_list):
            current_line = self._resume_lines_list[self._current_line_index]
            self._current_line_index += 1
            return current_line

        return None

    def get_sorted_lines(self):
        return sorted(
            self._resume_lines_list, key=lambda line: len(line.text), reverse=True
        )

    def extract_text_from_pdf(self) -> None:
        doc = fitz.open(stream=self._pdf_bytes, filetype="pdf")  # open document
        for page in doc:  # iterate the document pages
            page_content_blocks = page.get_text("blocks", sort=True)
            self._resume_text += page.get_text()
            for block in page_content_blocks:
                # block indexes according to the docs
                block_text = re.sub("\n|\n\s*| \s*", " ", block[4]).strip().split(".")

                if len(block_text) != 0:
                    for line in block_text:
                        self._resume_lines_list.append(
                            ResumeLine(line, block[0], block[2], block[1], block[3])
                        )

    def get_resume_lines_list(self) -> List[ResumeLine]:
        return self._resume_lines_list

    @property
    def resume_text(self) -> str:
        return self._resume_text

    @property
    def lines(self) -> List[ResumeLine]:
        return self._resume_lines_list
