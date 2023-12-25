import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple

from .booster import Booster
from .file_check import is_valid_resume
from .resume_parser import ResumeParser
from .test_result import FileTestResult


def boost_resume_to_json(pdf_bytes: bytes, user_id: str) -> Tuple[bool, int, str]:
    test_result: FileTestResult = is_valid_resume(pdf_bytes)
    if not test_result.is_passed():
        return test_result.status, 400, test_result.error_message

    parser: ResumeParser = ResumeParser(pdf_bytes)

    booster = Booster(user_id)

    try:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(booster.feedback_resume, parser.resume_text),
                executor.submit(booster.rephrase_lines, parser.resume_text),
            ]

            for future in as_completed(futures):  # type: ignore
                if future.exception():
                    raise future.exception()  # type: ignore

    except Exception as e:
        logging.info(f"An error occurred while making the API call: {e}")
        return (
            False,
            500,
            "Oops! something went wrong on our side, please check again later.",
        )

    return True, 200, booster.make_json()
