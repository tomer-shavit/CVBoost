from typing import Optional, List, Dict
import re
from .resume_line import ResumeLine
from re import Match


class Analyzer:
    SKILLS = "skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    EDUCATION = "education"
    HOBBIES = "hobbies"
    ACCOMPLISHMENTS = "accomplishments"
    MILITARY_SERVICE = "military service"

    def __init__(self, original_text: str):
        self._original_text = original_text
        self._skills: List[ResumeLine] = []
        self._experience: List[ResumeLine] = []
        self._projects: List[ResumeLine] = []
        self._education: List[ResumeLine] = []
        self._hobbies: List[ResumeLine] = []
        self._accomplishments: List[ResumeLine] = []
        self._military_service: List[ResumeLine] = []

    def get_analyzed_data(self) -> Dict[str, List[ResumeLine]]:
        return {self.SKILLS: self._skills, self.EXPERIENCE: self._experience, self.PROJECTS: self._projects,
                self.EDUCATION: self._education, self.HOBBIES: self._hobbies,
                self.ACCOMPLISHMENTS: self._accomplishments, self.MILITARY_SERVICE: self._military_service}

    @staticmethod
    def is_skills_section(line: str) -> bool:
        """
        Returns True if the given line of text is likely to be part of the "Skills"
        section of a resume, based on certain keywords and phrases commonly used
        in this section.
        """
        keywords = ["Skills", "competencies", "programming", "Technical Skills", "Professional Skills", "Areas of Expertise",
                    "Core Competencies"]
        for keyword in keywords:
            if re.search(keyword, line, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def is_education_section(line: str) -> bool:
        patterns = [
            'education',
            'academic',
            'educational background',
            'educational qualifications',
            'course',
            'educational credentials',
            'relevant coursework',
            'certifications',
            'certificates',
            'licences',
            'courses',
        ]
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def is_projects_section(line: str) -> bool:
        patterns = [
            'projects',
            'relevant projects',
            'side projects',
            'personal projects',
            'project highlights',
            'project work'
        ]
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def is_military_section(line: str) -> bool:
        military_keywords = ['Military', 'Military Service']
        line = line.strip().lower()
        for keyword in military_keywords:
            if re.search(keyword, line, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def is_experience_section(line: str) -> bool:
        patterns = [
            'experience',
            'work experience',
            'professional experience',
            'relevant experience',
            'employment history',
            'career history',
            'professional background',
            'work history',
            'related experience',
            'technical experience',
            'industry experience',
            'project experience',
            'professional summary',
            'career summary'
        ]
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def is_hobbies_section(line: str) -> bool:
        patterns = [
            'hobbies',
            'interests',
            'activities',
            'extracurricular activities',
            'volunteer work',
            'community involvement',
            "social experience"
            'personal interests',
        ]
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def is_accomplishments_section(line: str) -> bool:
        patterns = [
            'accomplishments',
            'achievements',
            'awards',
            'honors',
            'recognitions',
        ]
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def add_to_analyzer(self, line: ResumeLine, line_type: str) -> None:
        if line_type == self.SKILLS:
            self._skills.append(line)
        elif line_type == self.EXPERIENCE:
            self._experience.append(line)
        elif line_type == self.PROJECTS:
            self._projects.append(line)
        elif line_type == self.HOBBIES:
            self._hobbies.append(line)
        elif line_type == self.EDUCATION:
            self._education.append(line)
        elif line_type == self.ACCOMPLISHMENTS:
            self._accomplishments.append(line)
        elif line_type == self.MILITARY_SERVICE:
            self._military_service.append(line)

    @property
    def skills(self) -> List[ResumeLine]:
        return self._skills

    @property
    def experience(self) -> List[ResumeLine]:
        return self._experience

    @property
    def projects(self) -> List[ResumeLine]:
        return self._projects

    @property
    def education(self) -> List[ResumeLine]:
        return self._education

    @property
    def original_text(self) -> str:
        return self._original_text
