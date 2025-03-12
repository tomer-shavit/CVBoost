from enum import IntEnum

from .types.feedback_function import FeedbackFunction

from .types.rephrase_functions import RephraseFunction


class SystemType(IntEnum):
    BOOST = 1


class BoostVersion(IntEnum):
    V1 = 1


class PromptFactory:
    def __init__(self, language: str = 'fr') -> None:
        self.language = language
        
        # System prompts by language
        self.system_prompts = {
            'fr': {
                SystemType.BOOST: "Vous êtes un expert en conseil de carrière. Vous aidez à améliorer les CV des personnes depuis 20 ans."
            },
            'en': {
                SystemType.BOOST: "You're an expert career advisor. You've been helping improve people's resumes for 20 years."
            }
        }
        
        # Feedback prompts by language
        self.feedback_prompts = {
            'fr': {
                BoostVersion.V1: (
                    "Veuillez analyser mon CV et évaluer chacun des critères suivants sur 100 :\n"
                    "Clarté et lisibilité\nPertinence\nRéalisations\nMots-clés\n"
                    "Veuillez également fournir un résumé de mon CV et des suggestions d'amélioration."
                )
            },
            'en': {
                BoostVersion.V1: (
                    "Please analyze my resume and rate each of the following criteria out of 100:\n"
                    "Clarity and readability\nRelevance\nAchievements\nKeywords\n"
                    "Please also provide a summary of my resume and suggestions for improvement."
                )
            }
        }
        
        # Rephrase prompts by language
        self.rephrase_prompts = {
            'fr': (
                "Veuillez améliorer mon CV en le rendant plus professionnel et impactant. "
                "Conservez toutes les informations mais reformulez-les pour qu'elles soient plus efficaces. "
                "Concentrez-vous sur l'utilisation de verbes d'action et de mots-clés pertinents pour le secteur."
            ),
            'en': (
                "Please improve my resume by making it more professional and impactful. "
                "Keep all the information but rephrase it to be more effective. "
                "Focus on using action verbs and relevant keywords for the industry."
            )
        }
        
        # Function descriptions by language
        self.function_descriptions = {
            'fr': {
                'general_feedback': "Résumez les principaux points forts et points faibles de MON CV, avec des commentaires constructifs, en termes de :\nClarté\nLisibilité\nPertinence\nRéalisations\nMots-clés. Je suis le candidat, parlez-moi directement.",
                'clarity_feedback': "Est-ce que mon CV est facile à lire ? Les informations sont-elles présentées dans un ordre logique ? Y a-t-il quelque chose que je peux faire pour l'améliorer ? Donnez des exemples avec des citations. Je suis le candidat.",
                'clarity_score': "Score réaliste, non arrondi, sur 100 basé sur la clarté du CV",
                'relevance_feedback': "Les compétences et l'expérience listées sur mon CV sont-elles pertinentes pour le poste auquel je postule ? Y a-t-il des informations non pertinentes qui devraient être supprimées ? Donnez des exemples avec des citations. Je suis le candidat.",
                'relevance_score': "Score réaliste, non arrondi, sur 100 basé sur la pertinence du CV",
                'achievements_feedback': "Dans quelle mesure mes réalisations sont-elles mises en valeur ? Sont-elles quantifiables et bien décrites ? Que devrais-je changer pour l'améliorer ? Donnez des exemples avec des citations. Je suis le candidat.",
                'achievements_score': "Score réaliste, non arrondi, sur 100 basé sur la mise en valeur de mes réalisations",
                'keywords_feedback': "Ai-je inclus des mots-clés spécifiques à l'industrie qui feront ressortir mon CV auprès des employeurs et des systèmes de suivi des candidatures ? Que devrais-je changer pour l'améliorer ? Donnez des exemples avec des citations. Je suis le candidat.",
                'keywords_score': "Score réaliste, non arrondi, sur 100 basé sur la quantité de mots-clés utilisés dans le CV"
            },
            'en': {
                'general_feedback': "Summarize the main Pros and Cons of MY resume, with constructive feedback, in terms of:\nClarity\nReadability\nRelevance\nAchievements\nKeywords. I am the applicant, talk to me directly.",
                'clarity_feedback': "How easy is it to read the resume? Is the information presented in a logical order? Is there anything that i can do to improve it? Give examples with quotes. I am the applicant",
                'clarity_score': "Realistic, not rounded, score out of 100 based on how clear the resume is",
                'relevance_feedback': "Are the skills and experience listed on the resume relevant to the job I'm applying for? Is there any irrelevant information that should be removed? Give examples with quotes. I am the applicant",
                'relevance_score': "Realistic, not rounded, score out of 100 based on how relevant the resume is",
                'achievements_feedback': "How well have my accomplishments been highlighted? Are they quantifiable and well-described? What should i change to improve it? Give examples with quotes. I am the applicant",
                'achievements_score': "Realistic, not rounded, score out of 100 based on well my accomplishments are highlighted",
                'keywords_feedback': "Have I included industry-specific keywords that will make my resume stand out to employers and applicant tracking systems? What should i change to improve it? Give examples with quotes. I am the applicant",
                'keywords_score': "Realistic, not rounded, score out of 100 based on the amount of keywords used the resume"
            }
        }

    def build_system_prompt(self, type: SystemType) -> str:
        # Get the system prompt for the specified language, fallback to English if not available
        language_prompts = self.system_prompts.get(self.language, self.system_prompts['en'])
        return language_prompts.get(type, self.system_prompts['en'][type])

    def build_feedback_prompt(self, version: BoostVersion) -> str:
        # Get the feedback prompt for the specified language, fallback to English if not available
        language_prompts = self.feedback_prompts.get(self.language, self.feedback_prompts['en'])
        return language_prompts.get(version, self.feedback_prompts['en'][version])

    def build_repharse_prompt(self) -> str:
        # Get the rephrase prompt for the specified language, fallback to English if not available
        return self.rephrase_prompts.get(self.language, self.rephrase_prompts['en'])

    def build_feedback_function(self) -> FeedbackFunction:
        # Get the function descriptions for the specified language, fallback to English if not available
        descriptions = self.function_descriptions.get(self.language, self.function_descriptions['en'])
        
        return {
            "name": "get_feedback",
            "parameters": {
                "type": "object",
                "properties": {
                    "general_feedback": {
                        "type": "string",
                        "description": descriptions['general_feedback'],
                    },
                    "clarity": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": descriptions['clarity_feedback'],
                            },
                            "score": {
                                "type": "integer",
                                "description": descriptions['clarity_score'],
                            },
                        },
                    },
                    "relevance": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": descriptions['relevance_feedback'],
                            },
                            "score": {
                                "type": "integer",
                                "description": descriptions['relevance_score'],
                            },
                        },
                    },
                    "achievements": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": descriptions['achievements_feedback'],
                            },
                            "score": {
                                "type": "integer",
                                "description": descriptions['achievements_score'],
                            },
                        },
                    },
                    "keywords": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": descriptions['keywords_feedback'],
                            },
                            "score": {
                                "type": "integer",
                                "description": descriptions['keywords_score'],
                            },
                        },
                    },
                },
                "required": [
                    "general_feedback",
                    "clarity",
                    "relevance",
                    "achievements",
                    "keywords",
                ],
            },
        }

    @staticmethod
    def build_rephrase_function() -> RephraseFunction:
        return {
            "name": "get_feedback",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "old_line": {
                                    "type": "string",
                                    "description": "The needed to be improved line from the resume. For better Clarity, Skill, Relevance, Achievements portrayal, and keyword usage.",
                                },
                                "new_line": {
                                    "type": "string",
                                    "description": "The improved line you suggest. To enhance the resume's overall effectiveness in terms of Clarity, Skill, Relevance, Achievements, and Keyword usage.",
                                },
                            },
                            "required": ["old_line", "new_line"],
                        },
                    },
                    "number_of_lines": {
                        "type": "integer",
                        "description": "The number of lines you suggested to improve.",
                    },
                },
                "required": ["lines"],
            },
        }
