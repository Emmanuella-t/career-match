"""Domain errors for Career Match."""


class CareerMatchError(Exception):
    """Base error for Career Match ML operations."""


class SchemaError(CareerMatchError):
    """Raised when a resume record does not match the expected schema."""


class MatchingNotImplementedError(CareerMatchError):
    """Raised by ``UnimplementedMatcher`` when a caller requires a no-op sentinel.

    Prefer ``BaselineMatcher`` for the lexical v0.1 baseline. That baseline is
    still not a production hiring model.
    """
