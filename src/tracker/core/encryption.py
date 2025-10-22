"""Field-level encryption for sensitive data"""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet

from tracker.config import settings


class EncryptionService:
    """Service for encrypting/decrypting sensitive fields"""

    def __init__(self):
        self._fernet: Optional[Fernet] = None
        self._initialize()

    def _initialize(self):
        """Initialize encryption with key from settings or generate new"""
        key = settings.encryption_key

        if not key:
            # Generate new key if not configured
            new_key = Fernet.generate_key()
            key = new_key.decode()
            print(f"⚠️  Generated new encryption key. Add to .env: ENCRYPTION_KEY={key}")

        try:
            # Ensure key is in bytes format
            if isinstance(key, str):
                key = key.encode()
            self._fernet = Fernet(key)
        except Exception as e:
            # If key is invalid, generate a new one
            print(f"⚠️  Invalid encryption key, generating new one: {e}")
            new_key = Fernet.generate_key()
            key_str = new_key.decode()
            print(f"⚠️  Add to .env: ENCRYPTION_KEY={key_str}")
            self._fernet = Fernet(new_key)

    def encrypt(self, value: Optional[str]) -> Optional[str]:
        """Encrypt a string value"""
        if value is None:
            return None

        if not self._fernet:
            raise RuntimeError("Encryption not initialized")

        encrypted = self._fernet.encrypt(str(value).encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_value: Optional[str]) -> Optional[str]:
        """Decrypt an encrypted string"""
        if encrypted_value is None:
            return None

        if not self._fernet:
            raise RuntimeError("Encryption not initialized")

        try:
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = self._fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")


# Global encryption service instance
encryption_service = EncryptionService()
