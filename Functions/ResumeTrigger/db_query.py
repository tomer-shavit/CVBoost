from .db_connector import DBConnector
from .constants import *
import hashlib
import zlib
class DBQuery:
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector
        self.current_boost_id = -1

    def insert_resume_boost(self, user_id:str, boost_version:BoostVersion, resume_text:str) -> bool:
        query = """
        INSERT INTO ResumeBoost (userId, boostVersion, resumeHash)
        VALUES (%s, %s, %s)
        """
        resume_hash = self._hash_resume(resume_text)
        values = (user_id, int(boost_version), resume_hash)
        boost_id = self.db_connector.post(query, values)
        if not boost_id:
            return False
        self.current_boost_id = boost_id
        return True
        

    def insert_feedback(self, boost_id:int, feedback_type:FEEDBACK_TYPE, feedback_text:str, score:int , is_liked:bool) -> bool:
        query = """
        INSERT INTO Feedback (boostId, feedbackType, feedbackText, score, isLiked)
        VALUES (%s, %s, %s, %s, %s)
        """
        compressed_feedback = self._compress_text(feedback_text)
        values = (boost_id, int(feedback_type), compressed_feedback, score, is_liked)
        res = self.db_connector.post(query, values)
        if not res:
            return False
        return True
    
    def get_user(self, user_id: str) -> dict:
        query = """
        SELECT * FROM User WHERE id = %s
        """
        values = (user_id,)
        res = self.db_connector.get(query, values)
        if not res:
            return {}
        return res[0]
    
    def decrease_boost(self, user_id:str) -> bool:
        query = """
        UPDATE User
        SET resumeBoostsAvailable = resumeBoostsAvailable - 1
        WHERE id = %s
        """
        values = (user_id,)
        return bool(self.db_connector.post(query, values))

    def get_resume_by_hash(self, resume_text:str) -> dict:
        query = """
        SELECT * FROM ResumeBoost WHERE resumeHash = %s
        """
        values = (self._hash_resume(resume_text),)
        res = self.db_connector.get(query, values)
        if not res:
            return {}
        return res[0]
    
    @staticmethod
    def _hash_resume(resume: str) -> str:
        return hashlib.sha256(resume.encode()).hexdigest()
    
    @staticmethod
    def _compress_text(text: str) -> str:
        return zlib.compress(text.encode()).hex()

    @staticmethod
    def _decompress_text(text: str) -> str:
        return zlib.decompress(bytes.fromhex(text)).decode()