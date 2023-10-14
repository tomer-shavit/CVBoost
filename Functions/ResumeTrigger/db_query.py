from .db_connector import DBConnector
from .constants import *
import hashlib
import zlib
from .encrypter import Encrypter
import threading
class DBQuery:
    def __init__(self, db_connector: DBConnector, encrypter: Encrypter):
        self.db_connector = db_connector
        self.current_boost_id = -1
        self.encrypter = encrypter
        self.lock = threading.Lock()

    def insert_resume_boost(self, user_id:str, boost_version:BoostVersion, resume_text:str) -> int | None:
        with self.lock:
            compressed_text = self._compress_text(resume_text)
            encrypted_text = self.encrypter.encrypt(compressed_text)

            query = """
            INSERT INTO ResumeBoost (userId, boostVersion, resumeHash, resumeText, salt)
            VALUES (%s, %s, %s, %s, %s)
            """
            resume_hash = self._hash_resume(resume_text)
            values = (user_id, int(boost_version), resume_hash, encrypted_text, self.encrypter.salt)

            return self.db_connector.post(query, values)


    def insert_feedback(self, boost_id:int, feedback_type:FEEDBACK_TYPE, feedback_text:str, score:int , is_liked:bool ) -> bool:
       with self.lock: 
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
    
    def insert_line_feedback(self, boost_id:int, feedback_type:FEEDBACK_TYPE, feedback_text:str, is_liked:bool, feedback_text_reference: str) -> bool:
       with self.lock: 
            query = """
            INSERT INTO Feedback (boostId, feedbackType, feedbackText, feedbackTextReference, isLiked)
            VALUES (%s, %s, %s, %s, %s)
            """
            compressed_ref = self._compress_text(feedback_text_reference)
            encrypted_ref = self.encrypter.encrypt(compressed_ref)
            compressed_feedback = self._compress_text(feedback_text)
            values = (boost_id, int(feedback_type), compressed_feedback, encrypted_ref, is_liked)
            res = self.db_connector.post(query, values)
            if not res:
                return False
            return True
    
    def get_user(self, user_id: str) -> dict:
       with self.lock: 
            query = """
            SELECT * FROM User WHERE id = %s
            """
            values = (user_id,)
            res = self.db_connector.get(query, values)
            if not res:
                return {}
            return res[0]
    
    def decrease_boost(self, user_id:str) -> bool:
       with self.lock: 
            query = """
            UPDATE User
            SET resumeBoostsAvailable = resumeBoostsAvailable - 1
            WHERE id = %s
            """
            values = (user_id,)
            return bool(self.db_connector.post(query, values))

    def get_resume_by_hash(self, resume_text:str) -> dict:
       with self.lock: 
            query = """
            SELECT * FROM ResumeBoost WHERE resumeHash = %s
            """
            values = (self._hash_resume(resume_text),)
            res = self.db_connector.get(query, values)
            if not res:
                return {}
            return res[0]
    
    def delete_boost(self, boost_id: str) -> bool:
       with self.lock: 
            query = """
            DELETE FROM ResumeBoost WHERE id = %s
            """
            values = (boost_id)
            return bool(self.db_connector.post(query, values))  

    @staticmethod
    def _hash_resume(resume: str) -> str:
        return hashlib.sha256(resume.encode()).hexdigest()
    
    @staticmethod
    def _compress_text(text: str) -> str:
        return zlib.compress(text.encode()).hex()

    @staticmethod
    def _decompress_text(text: str) -> str:
        return zlib.decompress(bytes.fromhex(text)).decode()