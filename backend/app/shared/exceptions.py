"""
Shared exception classes used across modules. Routers catch these
and translate to HTTP responses.
"""


class NotFoundError(Exception):
    """Raised when a requested resource doesn't exist."""
    pass


class ExternalServiceError(Exception):
    """Raised when an external call (NVIDIA API, image-service) fails unrecoverably."""
    pass
