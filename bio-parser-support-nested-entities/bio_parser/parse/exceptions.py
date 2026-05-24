"""Exceptions raised during file parsing."""
from pathlib import Path


class FileProcessingError(Exception):
    """Raised when a problem is encountered while parsing a file."""

    filename: Path
    """
    Path of the file being processed.
    """

    def __init__(self, filename: Path, *args: object) -> None:
        super().__init__(*args)
        self.filename = filename


class InvalidFile(FileProcessingError):
    """Raised when the file is not valid."""

    def __str__(self) -> str:
        return f"BIO file {self.filename} is not valid"


class ForbiddenEntityName(FileProcessingError):
    """Raised when the file is not valid."""

    entity_name: str
    """
    Forbidden entity name encountered.
    """

    def __init__(self, filename: Path, entity_name: str, *args: object) -> None:
        super().__init__(filename=filename, *args)
        self.entity_name = entity_name

    def __str__(self) -> str:
        return f"Invalid entity name {self.entity_name}: reserved for global statistics ({self.filename})."
