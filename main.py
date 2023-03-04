from parser import Parser
from analyzer import Analyzer
import sys, fitz

def parse_resume(pdf_path: str) -> None:
    parser: Parser = Parser(pdf_path)
    analyzer: Analyzer = Analyzer()
    line_type: str = ""

    for line in parser.get_resume_lines_list():
        if analyzer.is_experience_section(line):
            line_type = analyzer.EXPERIENCE
        elif analyzer.is_skills_section(line):
            line_type = analyzer.SKILLS
        elif analyzer.is_projects_section(line):
            line_type = analyzer.PROJECTS
        elif analyzer.is_education_section(line):
            line_type = analyzer.EDUCATION
        elif analyzer.is_hobbies_section(line):
            line_type = analyzer.HOBBIES
        elif analyzer.is_accomplishments_section(line):
            line_type = analyzer.ACCOMPLISHMENTS

        analyzer.add_to_analyzer(line, line_type)


if __name__ == "__main__":
    parse_resume(sys.argv[1])







