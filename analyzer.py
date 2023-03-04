from typing import Optional, List, Dict, Any
import re
from re import Match


class Analyzer:
    SKILLS = "skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    EDUCATION = "education"
    HOBBIES = "hobbies"
    ACCOMPLISHMENTS = "accomplishments"
    MILITARY_SERVICE = "military service"

    def __init__(self):
        self._skills: List[str] = []
        self._experience: List[str] = []
        self._projects: List[str] = []
        self._education: List[str] = []
        self._hobbies: List[str] = []
        self._accomplishments: List[str] = []
        self._military_service: List[str] = []

    def get_analyzed_data(self) -> Dict[str, List[str]]:
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

    def add_to_analyzer(self, line: str, line_type: str) -> None:
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
    def skills(self) -> List[str]:
        return self._skills

    @property
    def experience(self) -> List[str]:
        return self._experience

    @property
    def projects(self) -> List[str]:
        return self._projects
