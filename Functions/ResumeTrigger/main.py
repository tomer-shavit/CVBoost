import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple

from .booster import Booster
from .db_connector import DBConnector
from .db_query import DBQuery
from .encrypter import Encrypter
from .file_check import is_valid_resume
from .resume_parser import ResumeParser
from .test_result import FileTestResult


def can_boost_resume(user_id: str, db_query: DBQuery) -> bool:
    user = db_query.get_user(user_id)
    if not user:
        return False
    return user["resumeBoostsAvailable"] > 0


def boost_resume_to_json(pdf_bytes: bytes, user_id: str) -> Tuple[bool, int, str]:
    test_result: FileTestResult = is_valid_resume(pdf_bytes)
    if not test_result.is_passed():
        return test_result.status, 400, test_result.error_message

    parser: ResumeParser = ResumeParser(pdf_bytes)
    db_connector = DBConnector()
    encrypter = Encrypter()
    db_query = DBQuery(db_connector, encrypter)

    if not can_boost_resume(user_id, db_query):
        return False, 400, "You have reached the maximum number of boosts"

    try:
        booster = Booster(user_id, parser.resume_text, db_query)
    except Exception as e:
        logging.info(f"An error occurred while creating the booster: {e}")
        return (
            False,
            500,
            "Oops! something went wrong on our side, please check again later.",
        )

    lines_to_rephrase = [line for line in parser.get_sorted_lines()[:4]]

    if booster.is_already_boosted():
        booster.recall_feedback()
        return True, 200, booster.make_json()

    try:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(booster.feedback_resume, parser.resume_text),
                executor.submit(booster.rephrase_lines, lines_to_rephrase),
            ]

            for future in as_completed(futures):  # type: ignore
                # Wait for all the API calls to complete
                if future.exception():
                    raise future.exception()  # type: ignore
    except Exception as e:
        logging.info(f"An error occurred while making the API call: {e}")
        # booster.delete_boost()
        return (
            False,
            500,
            "Oops! something went wrong on our side, please check again later.",
        )

    booster.decrease_boost()

    return True, 200, booster.make_json()
