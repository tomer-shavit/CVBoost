from .resume_parser import ResumeParser
from .analyzer import Analyzer
from .booster import Booster


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

    return analyzer


def boost_resume_to_json(path: str) -> str:
    analyzer = parse_resume(path)
    booster = Booster()
    booster.feedback_resume(analyzer.original_text)
    return booster.make_json()
