from typing import Optional
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

    def encrypt_sensative_text(self, text: str) -> str:
        compressed_text = self.compress_text(text)
        encrypted_text = self.encrypter.encrypt(compressed_text)
        return encrypted_text

    def decrypt_sensative_text(self, encrypted_text: str) -> str:
        compressed_text = self.encrypter.decrypt(encrypted_text)
        decrypted_text = self.decompress_text(compressed_text)
        return decrypted_text

    def insert_resume_boost(
        self, user_id: str, boost_version: BoostVersion, resume_text: str
    ) -> int:
        with self.lock:
            encrypted_text = self.encrypt_sensative_text(resume_text)
            query = """
            INSERT INTO ResumeBoost (userId, boostVersion, resumeHash, resumeText)
            VALUES (%s, %s, %s, %s)
            """
            resume_hash = self._hash_resume(resume_text)
            values = (
                user_id,
                int(boost_version),
                resume_hash,
                encrypted_text,
            )

            boost_id = self.db_connector.post(query, values)

            if not boost_id:
                raise Exception("Failed to insert resume boost")

            return boost_id

    def insert_feedback(
        self,
        boost_id: int,
        feedback_type: FEEDBACK_TYPE,
        feedback_text: str,
        score: int,
        is_liked: bool,
    ) -> int:
        with self.lock:
            query = """
            INSERT INTO Feedback (boostId, feedbackType, feedbackText, score, isLiked)
            VALUES (%s, %s, %s, %s, %s)
            """
            compressed_feedback = self.compress_text(feedback_text)
            values = (
                boost_id,
                int(feedback_type),
                compressed_feedback,
                score,
                is_liked,
            )
            feedback_id = self.db_connector.post(query, values)

            if not feedback_id:
                raise Exception("Failed to insert feedback")

            return feedback_id

    def insert_line_feedback(
        self,
        boost_id: int,
        feedback_type: FEEDBACK_TYPE,
        feedback_text: str,
        is_liked: bool,
        feedback_text_reference: str,
    ) -> int:
        with self.lock:
            query = """
            INSERT INTO Feedback (boostId, feedbackType, feedbackText, feedbackTextReference, isLiked)
            VALUES (%s, %s, %s, %s, %s)
            """
            compressed_ref = self.compress_text(feedback_text_reference)
            encrypted_ref = self.encrypter.encrypt(compressed_ref)
            compressed_feedback = self.compress_text(feedback_text)
            values = (
                boost_id,
                int(feedback_type),
                compressed_feedback,
                encrypted_ref,
                is_liked,
            )

            feedback_id = self.db_connector.post(query, values)

            if not feedback_id:
                raise Exception("Failed to insert feedback")

            return feedback_id

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

    def decrease_boost(self, user_id: str) -> int:
        with self.lock:
            query = """
            UPDATE User
            SET resumeBoostsAvailable = resumeBoostsAvailable - 1
            WHERE id = %s
            """
            values = (user_id,)
            boost_id = self.db_connector.post(query, values)

            if not boost_id:
                raise Exception("Failed to decrease num of boosts")

            return boost_id

    def get_boost_by_hash(self, resume_text: str) -> dict:
        with self.lock:
            query = """
            SELECT * FROM ResumeBoost WHERE resumeHash = %s
            """
            values = (self._hash_resume(resume_text),)
            res = self.db_connector.get(query, values)

            if not res:
                return {}

            return res[-1]

    def delete_boost(self, boost_id: int) -> int:
        with self.lock:
            query = """
            DELETE FROM ResumeBoost WHERE id = %s
            """
            values = (boost_id,)
            maybe_boost_id = self.db_connector.post(query, values)

            if not maybe_boost_id:
                raise Exception("Failed to delete boost")

            return maybe_boost_id

    @staticmethod
    def _hash_resume(resume: str) -> str:
        return hashlib.sha256(resume.encode()).hexdigest()

    @staticmethod
    def compress_text(text: str) -> str:
        return zlib.compress(text.encode()).hex()

    @staticmethod
    def decompress_text(text: str) -> str:
        return zlib.decompress(bytes.fromhex(text)).decode()

    def get_feedbacks(self, boostId: int) -> list:
        with self.lock:
            query = """
            SELECT * FROM Feedback WHERE boostId = %s
            """
            values = (str(boostId),)
            res = self.db_connector.get(query, values)

            return res
