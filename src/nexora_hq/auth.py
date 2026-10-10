"""Password hashing and signed cookie sessions for the HQ admin UI."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import sys
import time
from getpass import getpass

SESSION_TTL_SECONDS = 8 * 60 * 60
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password must not be empty")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32
    )
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, n_value, r_value, p_value, salt_hex, digest_hex = encoded_hash.split("$")
        n_value, r_value, p_value = int(n_value), int(r_value), int(p_value)
        if algorithm != "scrypt" or not (2**12 <= n_value <= 2**18) or not (1 <= r_value <= 16) or not (1 <= p_value <= 4):
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        if len(salt) != 16 or len(expected) != 32:
            return False
        actual = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=n_value, r=r_value, p=p_value, dklen=32
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, MemoryError):
        return False


def create_session(secret: str, now: int | None = None) -> str:
    issued_at = int(time.time()) if now is None else int(now)
    expires_at = issued_at + SESSION_TTL_SECONDS
    nonce = secrets.token_urlsafe(18)
    message = f"{expires_at}.{nonce}"
    signature = hmac.new(secret.encode("utf-8"), message.encode("ascii"), hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{message}.{encoded_signature}"


def verify_session(token: str | None, secret: str, now: int | None = None) -> bool:
    if not token:
        return False
    try:
        expires_value, nonce, supplied_signature = token.split(".")
        expires_at = int(expires_value)
        current_time = int(time.time()) if now is None else int(now)
        if expires_at <= current_time or not nonce or len(nonce) > 100:
            return False
        message = f"{expires_at}.{nonce}"
        signature = hmac.new(secret.encode("utf-8"), message.encode("ascii"), hashlib.sha256).digest()
        expected_signature = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
        return hmac.compare_digest(supplied_signature, expected_signature)
    except (ValueError, TypeError):
        return False


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] != "hash-password":
        raise SystemExit("Usage: python -m src.nexora_hq.auth hash-password")
    password = getpass("HQ admin password: ")
    confirmation = getpass("Confirm password: ")
    if not password or password != confirmation:
        raise SystemExit("Passwords must be non-empty and match")
    print(hash_password(password))


if __name__ == "__main__":
    main()
