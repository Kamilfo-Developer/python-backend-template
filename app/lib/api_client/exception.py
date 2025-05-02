"""API client exception."""


class BaseAPIClientException(Exception):
    """Base API client exception."""


class ClientError(BaseAPIClientException):
    """Client error."""
