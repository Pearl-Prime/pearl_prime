"""
Fernet encryption for brand admin credentials.

Credentials entered by brand admins are encrypted before storage.
Pearl_Int decrypts when auto-uploading content to platforms.
Admin never sees stored values after entry (vault pattern).

Key source: ADMIN_CREDENTIAL_KEY env var (32-byte base64-encoded Fernet key).
Generate a key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore
    logger.warning("cryptography package not installed — credential encryption unavailable")

REPO_ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = REPO_ROOT / "artifacts" / "admin_credentials"


def _get_key() -> Optional[bytes]:
    """Load Fernet key from env var or Keychain."""
    key_str = os.environ.get("ADMIN_CREDENTIAL_KEY", "")
    if not key_str:
        # Try Keychain
        try:
            import subprocess
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "phoenix-omega",
                 "-a", "ADMIN_CREDENTIAL_KEY", "-w"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                key_str = result.stdout.strip()
        except Exception:
            pass
    if not key_str:
        return None
    return key_str.encode("utf-8")


def encrypt_credentials(brand_id: str, credentials: dict[str, Any]) -> Path:
    """Encrypt and store brand admin credentials.

    Args:
        brand_id: Brand identifier (e.g., "inner_light_press_en_us")
        credentials: Dict of platform → {field: value} pairs

    Returns:
        Path to the encrypted file.

    Raises:
        RuntimeError: If encryption key is not available.
    """
    if Fernet is None:
        raise RuntimeError("cryptography package required: pip install cryptography")

    key = _get_key()
    if not key:
        raise RuntimeError(
            "ADMIN_CREDENTIAL_KEY not set. Generate with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )

    f = Fernet(key)
    plaintext = json.dumps(credentials, ensure_ascii=False).encode("utf-8")
    encrypted = f.encrypt(plaintext)

    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CREDENTIALS_DIR / f"{brand_id}.enc"
    out_path.write_bytes(encrypted)
    logger.info("Credentials encrypted for brand %s → %s", brand_id, out_path)
    return out_path


def decrypt_credentials(brand_id: str) -> Optional[dict[str, Any]]:
    """Decrypt and return brand admin credentials.

    Returns None if file doesn't exist or decryption fails.
    """
    if Fernet is None:
        logger.error("cryptography package not installed")
        return None

    key = _get_key()
    if not key:
        logger.error("ADMIN_CREDENTIAL_KEY not available")
        return None

    enc_path = CREDENTIALS_DIR / f"{brand_id}.enc"
    if not enc_path.exists():
        return None

    try:
        f = Fernet(key)
        decrypted = f.decrypt(enc_path.read_bytes())
        return json.loads(decrypted.decode("utf-8"))
    except (InvalidToken, json.JSONDecodeError) as e:
        logger.error("Failed to decrypt credentials for %s: %s", brand_id, e)
        return None


def has_credentials(brand_id: str) -> bool:
    """Check if encrypted credentials exist for a brand."""
    return (CREDENTIALS_DIR / f"{brand_id}.enc").exists()
