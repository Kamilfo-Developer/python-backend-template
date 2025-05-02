"""Security."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jwt import decode as jwt_decode, encode as jwt_encode


class JWTService:
    """JWTService utility class for encoding and decoding JSON Web Tokens."""

    def __init__(self, secret_key: str, jwt_algorithm: str) -> None:
        """Initialize the JWTService class with a secret key, algorithm, and expiration time.

        Args:
            secret_key (str): The secret key to sign the JWTService.
            jwt_algorithm (str): The algorithm to use for signing the JWTService.

        """
        self._secret_key = secret_key
        self._jwt_algorithm = jwt_algorithm

    def encode(
        self,
        data: Any,
        expires_in: int | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        """Encode data into a JWTService.

        Args:
            data (Any): The data to encode into the JWTService.
            expires_in (int | None, optional): The expiration time in minutes. Defaults to None.

        Returns:
            str: The encoded JWTService.

        """
        payload: dict[str, Any] = {"sub": str(data)} | (kwargs or {})

        if expires_in is not None:
            payload["exp"] = datetime.now(UTC) + timedelta(minutes=expires_in)

        return jwt_encode(payload, self._secret_key, algorithm=self._jwt_algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        """Decode a JWTService.

        Args:
            token (str): The JWTService to decode.

        Returns:
            dict[str, Any]: The decoded data.

        """
        return jwt_decode(token, key=self._secret_key, algorithms=[self._jwt_algorithm])
