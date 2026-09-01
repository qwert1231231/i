"""Public interface for the I language interpreter."""

from .interpreter import run_code, run_file

__version__ = "0.1.0"

__all__ = ["run_code", "run_file", "__version__"]
