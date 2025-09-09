"""JWT service for token generation and validation.

This module provides services for JWT (JSON Web Token) handling,
including token generation, validation, and decoding.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jwt import decode as jwt_decode
from jwt import encode as jwt_encode
from pydantic import BaseModel


class JWTService:
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
        data: BaseModel,
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
        payload: dict[str, Any] = {"sub": data.model_dump_json()}

        if additional_claims:
            payload.update(additional_claims)

        if expires_in is not None:
            payload["exp"] = datetime.now(UTC) + timedelta(minutes=expires_in)

        return jwt_encode(payload, self._secret_key, algorithm=self._jwt_algorithm)

    def decode[T: BaseModel](self, token: str, model: type[T], required_claims: list[str] | None = None) -> T:
        """Decode a JWT and validate required claims.

        Args:
            token: The JWT string to decode
            model: The model to decode the JWT into
            required_claims: The required claims to validate

        Returns:
            The decoded JWT payload as a dictionary

        Raises:
            jwt.exceptions.InvalidTokenError: If the token is invalid
            jwt.exceptions.ExpiredSignatureError: If the token has expired

        """
        payload = jwt_decode(
            token,
            key=self._secret_key,
            algorithms=[self._jwt_algorithm],
            options={
                "require": required_claims,
            },
        )

        return model.model_validate_json(
            payload["sub"],
        )
