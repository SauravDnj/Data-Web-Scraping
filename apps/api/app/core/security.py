"""Low-level identity primitives (password hashing, email
normalization). Not authentication service logic — no login/token
issuance here; that's T038's job. This just gives the persistence
layer (T022) something to store that is never plaintext."""

import bcrypt


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode(
        "ascii"
    )


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("ascii"))
