from typing import Optional, List, Dict, Any
import re
from re import Match


class Analyzer:
    SKILLS = "skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    EDUCATION = "education"


    def __init__(self):
        self._skills: List[str] = []
        self._experience: List[str] = []
        self._projects: List[str] = []
        self._education: List[str] = []

    def is_skills_section(line: str) -> bool:
        """
        Returns True if the given line of text is likely to be part of the "Skills"
        section of a resume, based on certain keywords and phrases commonly used
        in this section.
        """
        keywords = ["Skills", "Technical Skills", "Professional Skills", "Areas of Expertise", "Core Competencies"]
        for keyword in keywords:
            if keyword in line:
                return True
        return False

    def add_to_analyzer(self, line: str, type: str) -> None:
        if type == self.SKILLS:
            self._skills.append(line)
        elif type == self.EXPERIENCE:
            self._experience.append(line)
        if type == self.PROJECTS:
            self._projects.append(line)

    @property
    def skills(self) -> List[str]:
        return self._skills

    @property
    def experience(self) -> List[str]:
        return self._experience

    @property
    def projects(self) -> List[str]:
        return self._projects
