"""Validates the construction of the BIO file."""
import json
import logging
from dataclasses import asdict
from pathlib import Path

from bio_parser.parse.document import Document
from bio_parser.parse.nested_document import NestedDocument

logger = logging.getLogger(__name__)


def run(filepaths: list[Path], allow_nested=False) -> None:
    """Validate the construction of multiple BIO files.

    Args:
        filepaths (list[Path]): Files to check.
    """
    for filepath in filepaths:
        logger.info(f"Parsing file @ `{filepath}`")
        try:
            doc = (
                NestedDocument.from_file(filepath)
                if allow_nested
                else Document.from_file(filepath)
            )
            filepath.with_suffix(".json").write_text(json.dumps(asdict(doc), indent=2))
            logger.info(f"The file @ `{filepath}` is valid!")

        except Exception as e:
            logger.error(f"Could not load the file @ `{filepath}`: {e}")
