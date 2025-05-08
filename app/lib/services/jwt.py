"""JWT service for token generation and validation.

This module provides services for JWT (JSON Web Token) handling,
including token generation, validation, and decoding.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Generic, TypeVar

from jwt import decode as jwt_decode, encode as jwt_encode


T = TypeVar("T")


class JWTService(Generic[T]):
    """JWT service for encoding and decoding JSON Web Tokens.

    This service handles the creation and validation of JWTs,
    providing a secure way to transmit information between parties.
    """

    def __init__(self, secret_key: str, jwt_algorithm: str) -> None:
        """Initialize the JWT service.

        Args:
            secret_key: The secret key used to sign the JWT
            jwt_algorithm: The algorithm used for signing the JWT (e.g., 'HS256')

        """
        self._secret_key = secret_key
        self._jwt_algorithm = jwt_algorithm

    def encode(
        self,
        data: T,
        expires_in: int | None = None,
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        """Encode data into a JWT.

        Args:
            data: The data to encode into the JWT
            expires_in: The expiration time in minutes (optional)
            additional_claims: Additional claims to include in the JWT payload

        Returns:
            The encoded JWT string

        """
        payload: dict[str, Any] = {"sub": str(data)}

        if additional_claims:
            payload.update(additional_claims)

        if expires_in is not None:
            payload["exp"] = datetime.now(UTC) + timedelta(minutes=expires_in)

        return jwt_encode(payload, self._secret_key, algorithm=self._jwt_algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        """Decode a JWT.

        Args:
            token: The JWT string to decode

        Returns:
            The decoded JWT payload as a dictionary

        Raises:
            jwt.exceptions.InvalidTokenError: If the token is invalid
            jwt.exceptions.ExpiredSignatureError: If the token has expired

        """
        return jwt_decode(token, key=self._secret_key, algorithms=[self._jwt_algorithm])
