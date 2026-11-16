from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pwdlib.exceptions import HashVerificationError, UnknownHashError

from department_ai.core.config.settings import Settings

_password_hash = PasswordHash.recommended()
_dummy_password_hash = _password_hash.hash("not-a-real-account-password")
_algorithm = "HS256"


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, encoded_hash: str | None) -> bool:
    password_hash = encoded_hash or _dummy_password_hash
    try:
        return _password_hash.verify(password, password_hash)
    except (HashVerificationError, UnknownHashError, ValueError):
        return False


def create_access_token(user_id: UUID, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=_algorithm,
    )


def decode_access_token(token: str, settings: Settings) -> UUID:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[_algorithm],
        options={"require": ["exp", "sub"]},
    )
    subject = payload.get("sub")
    try:
        return UUID(subject)
    except (TypeError, ValueError) as error:
        raise InvalidTokenError("Invalid token subject") from error
