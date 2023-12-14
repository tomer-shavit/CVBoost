import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import hashlib
import os
import base64
from dotenv import load_dotenv  # type: ignore

load_dotenv()  # Load environment variables from .env file


class Encrypter:
    def __init__(self):
        self.seed = os.getenv("ENCRYPTION_SEED")

        if not self.seed:
            raise ValueError("ENCRYPTION_SEED not found in environment variables")

    def encrypt(self, plain_text: str) -> str:
        hashed_key = hashlib.sha256(self.seed.encode()).digest()

        iv = os.urandom(16)

        # Pad the text to be a multiple of 16 bytes (128 bits)
        padder = padding.PKCS7(128).padder()
        padded_text = padder.update(plain_text.encode()) + padder.finalize()

        # Encrypt the text
        cipher = Cipher(
            algorithms.AES(hashed_key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_text = encryptor.update(padded_text) + encryptor.finalize()

        # Return the IV and encrypted text encoded in Base64 to ensure easy transport
        return base64.b64encode(iv + encrypted_text).decode()

    def decrypt(self, encrypted_base64: str) -> str:
        encrypted_data = base64.b64decode(encrypted_base64)

        # Extract the IV and the encrypted text
        iv = encrypted_data[:16]
        encrypted_text = encrypted_data[16:]

        # Hash the key using SHA-256 to ensure it's 256 bits long
        hashed_key = hashlib.sha256(self.seed.encode()).digest()

        # Decrypt the text
        cipher = Cipher(
            algorithms.AES(hashed_key), modes.CBC(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_text = decryptor.update(encrypted_text) + decryptor.finalize()

        # Unpad the text
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_text = unpadder.update(padded_text) + unpadder.finalize()

        # Return the decrypted text as a string
        return decrypted_text.decode()
