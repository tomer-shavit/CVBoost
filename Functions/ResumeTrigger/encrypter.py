import os
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Encrypter:
    def __init__(self):
        self.seed = os.getenv("ENCRYPTION_SEED")
        self.salt = os.urandom(16)
        if not self.seed:
            raise ValueError("ENCRYPTION_SEED not found in environment variables")
        
        self.cipher = None
        self.init_cipher()

    def init_cipher(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt= self.salt, 
            iterations=100000,
            backend=default_backend()
        )
        key = urlsafe_b64encode(kdf.derive(self.seed.encode()))
        self.cipher = Fernet(key)
        

    def encrypt(self, plain_text: str) -> str:
        return self.cipher.encrypt(plain_text.encode()).decode()

    def decrypt(self, encrypted_text: str) -> str:
        return self.cipher.decrypt(encrypted_text.encode()).decode()

    def set_salt(self, salt: bytes) -> None:
        self.salt = salt
    
    def get_salt(self) -> bytes:
        return self.salt
