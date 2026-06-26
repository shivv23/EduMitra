import pytest
from src.utils.encryption import encrypt_field, decrypt_field, hash_phone


class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        plain = "Test Student Name"
        encrypted = encrypt_field(plain)
        decrypted = decrypt_field(encrypted)
        assert decrypted == plain

    def test_encrypt_empty_string(self):
        assert encrypt_field("") == b""
        assert decrypt_field(b"") == ""

    def test_encrypt_phone_number(self):
        plain = "+919876543210"
        encrypted = encrypt_field(plain)
        assert encrypted != plain.encode()
        assert decrypt_field(encrypted) == plain

    def test_hash_phone_consistency(self):
        phone = "+919876543210"
        assert hash_phone(phone) == hash_phone(phone)
        assert hash_phone(phone) != hash_phone("+911234567890")

    def test_encrypted_output_differs_from_input(self):
        plain = "Sensitive PII Data"
        encrypted = encrypt_field(plain)
        assert encrypted != plain.encode()
