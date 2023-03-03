import sys
from parser import Parser


def parse_resume(pdf_path: str) -> None:
    parser: Parser = Parser(pdf_path)
    # print(parser.get_resume_paragraphs_list())
    # for line in parser.get_resume_paragraphs_list():
    #     print(line + "\n------")
    for line in parser.get_resume_lines_list():
        print(line + "\n------")





if __name__ == "__main__":
    parse_resume(sys.argv[1])
