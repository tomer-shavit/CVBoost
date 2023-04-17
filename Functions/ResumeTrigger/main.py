from .resume_parser import ResumeParser
from .booster import Booster
from concurrent.futures import ThreadPoolExecutor, as_completed


def boost_resume_to_json(path: str) -> str:
    parser: ResumeParser = ResumeParser(path)
    booster = Booster()
    filtered_lines = [line for line in parser.get_sorted_lines()[:15] if line.text[-1] == "."]
    lines_to_rephrase = filtered_lines[:5]

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(booster.feedback_resume, parser.resume_text),
                   executor.submit(booster.rephrase_lines, lines_to_rephrase)]

        for future in as_completed(futures):
            # Wait for all the API calls to complete
            pass

    return booster.make_json()
