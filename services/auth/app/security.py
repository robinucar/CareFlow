from secrets import randbelow

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def generate_verification_code() -> str:
    return f"{randbelow(1_000_000):06d}"


def hash_verification_code(code: str) -> str:
    return password_hash.hash(code)


def verify_verification_code(code: str, code_hash: str) -> bool:
    return password_hash.verify(code, code_hash)
