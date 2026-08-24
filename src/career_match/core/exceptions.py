"""Domain errors for Career Match."""


class CareerMatchError(Exception):
    """Base error for Career Match ML operations."""


class SchemaError(CareerMatchError):
    """Raised when a resume record does not match the expected schema."""


class MatchingNotImplementedError(CareerMatchError):
    """Raised because no production resume-to-job matcher exists yet.

    The next milestone is a measurable lexical baseline, not this placeholder.
    """
