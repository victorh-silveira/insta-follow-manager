"""Domain-level exceptions for Insta Follow Manager."""


class DomainError(Exception):
    """Base exception for all domain errors."""


class ProfileNotFoundError(DomainError):
    """Raised when a target Instagram profile is not found in local storage."""


class NotFollowingError(DomainError):
    """Raised when attempting to unfollow a profile that is not currently followed."""


class GatewayError(DomainError):
    """Raised when communication with the Instagram gateway fails."""


class GatewayAuthError(GatewayError):
    """Raised when Instagram authentication or session validation fails."""


class RateLimitError(GatewayError):
    """Raised when Instagram rate limits or blocks the request."""
