import os

from resume_parser import ResumeParser
from analyzer import Analyzer
import sys
from booster import Booster


def parse_resume(pdf_path: str) -> Analyzer:
    parser: ResumeParser = ResumeParser(pdf_path)
    analyzer: Analyzer = Analyzer(parser.resume_text)
    text_type: str = ""

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

    # for key, value in analyzer.get_analyzed_data().items():
    #     print(key)
    #     for val in value:
    #         print("- " + val.text)
    return analyzer


if __name__ == "__main__":
    analyzer = parse_resume(sys.argv[1])
    booster = Booster()
    # print(os.getenv("GPT_API_KEY1"))
    resume_line_len = lambda x: len(x.text)
    skill = max(analyzer.skills, key=resume_line_len)
    booster.rephrase_line(skill)
    exp = max(analyzer.experience, key=resume_line_len)
    booster.rephrase_line(exp)
    print(booster.feedback_resume(analyzer.original_text))
