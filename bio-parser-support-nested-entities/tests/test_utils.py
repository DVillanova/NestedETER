from pathlib import Path

import pytest
from bio_parser.parse.document import Document
from bio_parser.utils import check_complete, check_valid_bio, load_dataset

from tests import FIXTURES

DATA = FIXTURES / "utils"


@pytest.mark.parametrize(
    "filenames",
    [
        (
            [
                DATA / "bad_format.bio",
            ]
        ),
        (
            [
                DATA / "bad_entity_name.bio",
            ]
        ),
        (
            [
                DATA / "labels" / "example_0.bio",
                DATA / "labels" / "example_1.bio",
                DATA / "labels" / "example_2.bio",
                DATA / "bad_entity_name.bio",
            ]
        ),
    ],
)
def test_check_valid_bio_raise(filenames):
    with pytest.raises(Exception):  # noqa: PT011
        check_valid_bio(filenames)


@pytest.mark.parametrize(
    "filenames",
    [
        (
            [
                DATA / "labels" / "example_0.bio",
                DATA / "labels" / "example_1.bio",
                DATA / "labels" / "example_2.bio",
            ]
        ),
        (
            [
                DATA / "predictions" / "example_0.bio",
                DATA / "predictions" / "example_1.bio",
                DATA / "predictions" / "example_2.bio",
            ]
        ),
        ([]),
    ],
)
def test_check_valid_bio(filenames):
    check_valid_bio(filenames)


@pytest.mark.parametrize(
    ("labels", "predictions"),
    [
        (
            [
                DATA / "labels" / "example_0.bio",
                DATA / "labels" / "example_1.bio",
                DATA / "labels" / "example_2.bio",
            ],
            [
                DATA / "predictions" / "example_0.bio",
                DATA / "predictions" / "example_1.bio",
                DATA / "predictions" / "example_2.bio",
            ],
        ),
        (
            [],
            [],
        ),
    ],
)
def test_check_complete(labels, predictions):
    check_complete(labels, predictions)


@pytest.mark.parametrize(
    ("labels", "predictions", "message"),
    [
        (
            [
                DATA / "labels" / "example_0.bio",
                DATA / "labels" / "example_1.bio",
                DATA / "labels" / "example_2.bio",
            ],
            [
                DATA / "predictions" / "example_0.bio",
                DATA / "predictions" / "example_1.bio",
            ],
            "Missing prediction files: {'example_2.bio'}.",
        ),
        (
            [
                DATA / "labels" / "example_0.bio",
                DATA / "labels" / "example_2.bio",
            ],
            [
                DATA / "predictions" / "example_0.bio",
                DATA / "predictions" / "example_1.bio",
                DATA / "predictions" / "example_2.bio",
            ],
            "Missing label files: {'example_1.bio'}.",
        ),
        (
            [
                DATA / "labels" / "example_0.bio",
                DATA / "labels" / "example_2.bio",
            ],
            [
                DATA / "predictions" / "example_1.bio",
                DATA / "predictions" / "example_2.bio",
            ],
            "Missing prediction files: {'example_0.bio'}.\nMissing label files: {'example_1.bio'}.",
        ),
    ],
)
def test_check_complete_raise(labels, predictions, message):
    with pytest.raises(FileNotFoundError, match=message):
        check_complete(labels, predictions)


@pytest.mark.parametrize(
    ("label_dir", "prediction_dir", "expected_names"),
    [
        (
            DATA / "labels",
            DATA / "predictions",
            [Path("example_0.bio"), Path("example_1.bio"), Path("example_2.bio")],
        ),
    ],
)
def test_load_dataset(label_dir, prediction_dir, expected_names):
    documents = load_dataset(label_dir, prediction_dir)
    for i, expected_name in enumerate(expected_names):
        assert documents[i] == (
            Document.from_file(label_dir / expected_name),
            Document.from_file(prediction_dir / expected_name),
        )
        assert documents[i][0].filename == expected_name.stem
        assert documents[i][1].filename == expected_name.stem


@pytest.mark.parametrize(
    ("label_dir", "prediction_dir", "message"),
    [
        (
            DATA / "labels_empty",
            DATA / "predictions",
            "Empty label directory",
        ),
        (
            DATA / "labels",
            DATA / "predictions_empty",
            "Empty prediction directory",
        ),
    ],
)
def test_load_empty_dataset(label_dir, prediction_dir, message):
    with pytest.raises(FileNotFoundError, match=f"^{message}: .*"):
        load_dataset(label_dir, prediction_dir)
