"""Shared auth utilities (password hashing)."""
import hashlib

SALT = "erp_salt"


def hash_password(password: str) -> str:
    return hashlib.sha256((password + SALT).encode()).hexdigest()


def check_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash
