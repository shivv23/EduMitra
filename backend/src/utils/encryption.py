from cryptography.fernet import Fernet
import hashlib
import base64
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)

_cipher = None


def _get_cipher() -> Fernet:
    global _cipher
    if _cipher is None:
        try:
            key = settings.encryption_key.encode()
            if len(key) != 44:
                key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
            _cipher = Fernet(key)
        except Exception as e:
            logger.error("Failed to initialize encryption cipher: %s", e)
            raise
    return _cipher


def encrypt_field(plaintext: str) -> bytes:
    if not plaintext:
        return b""
    return _get_cipher().encrypt(plaintext.encode())


def decrypt_field(ciphertext: bytes) -> str:
    if not ciphertext:
        return ""
    return _get_cipher().decrypt(ciphertext).decode()


def hash_phone(phone: str) -> str:
    return hashlib.sha256(phone.encode()).hexdigest()
