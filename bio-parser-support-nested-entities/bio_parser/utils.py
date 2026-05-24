"""Utils functions."""

import logging
from operator import attrgetter
from pathlib import Path

from bio_parser.parse.document import Document
from bio_parser.parse.exceptions import ForbiddenEntityName, InvalidFile

logger = logging.getLogger(__name__)


def check_complete(labels: list[Path], predictions: list[Path]):
    """Check that each label BIO file has a corresponding prediction BIO file and each prediction BIO file has a corresponding label BIO file. Otherwise raise an error.

    Args:
        labels: List of sorted label BIO files.
        predictions: List of sorted prediction BIO files.
    """
    # List filenames in prediction and label directories.
    label_filenames = {label.name for label in labels}
    prediction_filenames = {prediction.name for prediction in predictions}

    # Raise an error if there are any missing files.
    if label_filenames != prediction_filenames:
        messages = []
        missing_label_files = prediction_filenames.difference(label_filenames)
        missing_pred_files = label_filenames.difference(prediction_filenames)
        if len(missing_pred_files) > 0:
            messages.append(f"Missing prediction files: {missing_pred_files}.")
        if len(missing_label_files) > 0:
            messages.append(f"Missing label files: {missing_label_files}.")
        raise FileNotFoundError("\n".join(messages))


def check_valid_bio(
    bio_files: list[Path], global_stat_name: str | None = None
) -> list[Document]:
    """Check that BIO files exists and are valid.

    Args:
        bio_files (list[Path]): List of BIO files to check
        global_stat_name (str | None, optional): Forbid an entity name. Defaults to None.

    Raises:
        FileNotFoundError: A file could not be found.
        FileNotFoundError:
        Exception: Forbidden entity name used in a file.

    Returns:
        list[Document]: _description_
    """
    parsed = []
    for filename in bio_files:
        # Raise an error if the document does not exist
        if not filename.exists():
            raise FileNotFoundError(
                f"BIO file {filename} does not exist.",
            )

        # Raise an error if the document is not valid
        try:
            document = Document.from_file(filename)
        except Exception as e:
            raise InvalidFile(filename) from e

        # Raise an error if an entity is named global_stat_name
        if global_stat_name and global_stat_name in {
            entity[0] for entity in document.entities
        }:
            raise ForbiddenEntityName(filename=filename, entity_name=global_stat_name)
        parsed.append(document)
    return parsed


def load_dataset(
    label_dir: Path,
    prediction_dir: Path,
) -> list[tuple[Document, Document]]:
    """Load BIO files for a given dataset.

    Args:
        label_dir (Path): Path to the label directory.
        prediction_dir (Path): Path to prediction directory.

    Returns:
        A list of tuple containing the label and corresponding prediction Documents.
    """
    sorted_labels = sorted(label_dir.glob("*.bio"), key=attrgetter("name"))
    sorted_predictions = sorted(prediction_dir.glob("*.bio"), key=attrgetter("name"))

    # Check if a directory is empty
    if not (sorted_labels and sorted_predictions):
        messages = []
        if not sorted_labels:
            messages.append(f"Empty label directory: {label_dir}.")
        if not sorted_predictions:
            messages.append(f"Empty prediction directory: {prediction_dir}.")
        raise FileNotFoundError("\n".join(messages))

    # Check that the dataset is complete and valid
    check_complete(sorted_labels, sorted_predictions)

    logger.info("Loading labels...")
    labels = check_valid_bio(sorted_labels)

    logger.info("Loading prediction...")
    predictions = check_valid_bio(sorted_predictions)

    logger.info("The dataset is complete and valid.")
    # Return each label and prediction Document couple
    return list(zip(labels, predictions))
