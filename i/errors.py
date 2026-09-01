"""Custom exceptions and error reporting for the I language."""


class ILanguageError(Exception):
    """Base class for interpreter errors."""


class TokenError(ILanguageError):
    """Raised when tokenization fails."""


class ParseError(ILanguageError):
    """Raised when parsing fails."""


class RuntimeError(ILanguageError):
    """Raised when execution fails."""
