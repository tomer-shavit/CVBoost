import sys

from resume_parser import ResumeParser
from analyzer import Analyzer
from booster import Booster
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_resume(pdf_path: str) -> Analyzer:
    parser: ResumeParser = ResumeParser(pdf_path)
    analyzer: Analyzer = Analyzer(parser.resume_text)
    # parser.get_resume_paragraphs()
    # for par in parser.paragraphs:
    #     print(par)
    #     print()

    text_type: str = ""
    a = parser.get_resume_lines_list()

    for line in parser.get_resume_lines_list():
        if analyzer.is_experience_section(line.text):
            text_type = analyzer.EXPERIENCE
        elif analyzer.is_skills_section(line.text):
            text_type = analyzer.SKILLS
        elif analyzer.is_projects_section(line.text):
            text_type = analyzer.PROJECTS
        elif analyzer.is_education_section(line.text):
            text_type = analyzer.EDUCATION
        elif analyzer.is_hobbies_section(line.text):
            text_type = analyzer.HOBBIES
        elif analyzer.is_accomplishments_section(line.text):
            text_type = analyzer.ACCOMPLISHMENTS

        analyzer.add_to_analyzer(line, text_type)

    return analyzer


# def boost_resume_to_json(path: str) -> str:
#     parser: ResumeParser = ResumeParser(path)
#     booster = Booster()
#     filtered_lines = [line for line in parser.get_sorted_lines()[:15] if line.text[-1] == "."]
#     booster.rephrase_lines(filtered_lines[:5])
#     booster.feedback_resume(parser.resume_text)
#     return booster.make_json()


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

if __name__ == "__main__":
    json = boost_resume_to_json(sys.argv[1])
    print(json)
    print("niceeee")
