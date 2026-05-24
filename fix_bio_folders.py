#!/usr/bin/env python3
"""Create dummy BIO files so hypotheses and labels share the same filenames.

The script runs in this order:
1) For every `.bio` in hypotheses missing in labels, create it in labels.
2) Then for every `.bio` in labels missing in hypotheses, create it in hypotheses.

Each created file contains one dummy line:

    a O
"""
from __future__ import annotations

import argparse
from pathlib import Path

DUMMY_CONTENT = "a O\n"


def _collect_bio_filenames(folder: Path) -> set[str]:
    return {p.name for p in folder.iterdir() if p.is_file() and p.suffix == ".bio"}


def _create_missing_files(source_dir: Path, target_dir: Path) -> int:
    source_files = _collect_bio_filenames(source_dir)
    target_files = _collect_bio_filenames(target_dir)
    missing_in_target = sorted(source_files - target_files)

    for filename in missing_in_target:
        target = target_dir / filename
        target.write_text(DUMMY_CONTENT, encoding="utf-8")

    return len(missing_in_target)


def fix_bio_folders(hypotheses_dir: Path, labels_dir: Path) -> tuple[int, int]:
    if not hypotheses_dir.exists() or not hypotheses_dir.is_dir():
        raise ValueError(
            f"Hypotheses folder does not exist or is not a directory: {hypotheses_dir}"
        )
    if not labels_dir.exists() or not labels_dir.is_dir():
        raise ValueError(
            f"Labels folder does not exist or is not a directory: {labels_dir}"
        )

    created_in_labels = _create_missing_files(hypotheses_dir, labels_dir)
    created_in_hypotheses = _create_missing_files(labels_dir, hypotheses_dir)

    return created_in_labels, created_in_hypotheses


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Make hypotheses and labels contain the same .bio filenames "
            "by creating missing files in both directions."
        )
    )
    parser.add_argument(
        "--hypotheses-dir",
        type=Path,
        default=Path("hypotheses"),
        help="Path to hypotheses folder (default: hypotheses).",
    )
    parser.add_argument(
        "--labels-dir",
        type=Path,
        default=Path("labels"),
        help="Path to labels folder (default: labels).",
    )
    args = parser.parse_args()

    created_in_labels, created_in_hypotheses = fix_bio_folders(
        args.hypotheses_dir, args.labels_dir
    )
    print(
        f"Created {created_in_labels} missing .bio file(s) in {args.labels_dir} "
        f"and {created_in_hypotheses} missing .bio file(s) in {args.hypotheses_dir}."
    )


if __name__ == "__main__":
    main()
