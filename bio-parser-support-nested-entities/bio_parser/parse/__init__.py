"""
Validate a given BIO file.
"""

from argparse import ArgumentParser
from pathlib import Path

import yaml

from bio_parser.parse.validate import run


def _check_bio_ext(filename: str) -> Path:
    filepath = Path(filename)
    assert filepath.suffix == ".bio"
    return filepath


def _load_yaml(config: str) -> Path:
    with Path(config).open() as file:
        return yaml.safe_load(file)


def add_validate_parser(subcommands):
    parser: ArgumentParser = subcommands.add_parser(
        "validate",
        help=__doc__,
        description=__doc__,
    )
    parser.set_defaults(func=run)

    parser.add_argument(
        "filepaths", help="Files to validate.", type=_check_bio_ext, nargs="*"
    )
    parser.add_argument(
        "--allow-nested",
        help="Whether to allow nested entities.",
        action="store_true",
        default=False,
    )
