"""
Exception hierarchy for SATB splitting operations.
"""


class SATBSplitError(Exception):
    """Base exception for SATB splitting errors."""
    pass


class InvalidScoreError(SATBSplitError):
    """Raised when input score is not valid for SATB splitting."""
    pass


class VoiceDetectionError(SATBSplitError):
    """Raised when SATB voices cannot be detected."""
    pass


class VoiceRemovalError(SATBSplitError):
    """Raised when voice removal fails."""
    pass


class StaffSimplificationError(SATBSplitError):
    """Raised when staff simplification fails."""
    pass


class UnificationError(SATBSplitError):
    """Raised when unification process fails."""
    pass


class ProcessingError(SATBSplitError):
    """Raised when overall processing fails."""
    pass


class ValidationError(SATBSplitError):
    """Raised when validation fails."""
    pass