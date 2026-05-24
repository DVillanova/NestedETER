"""Convert bio-parser JSON output files into .pkl hierarchy lists.

For every .json file in the given folder, the script reads its ``hierarchy``
field, converts it into a nested list representation and writes a sibling
.pkl file in the same folder. Non-JSON files are ignored, so this script
is safe to run on folders that also contain .bio inputs or previously
generated .pkl outputs.
"""
from __future__ import annotations

import json
import os
import pickle
import sys
from pathlib import Path


def process_nested_ne(ne: dict) -> list:
    ne_tree = []
    ne_tree.append(ne["category"])
    ne_tree.append([])

    for child in ne["children"]:
        if isinstance(child, str):
            ne_tree[1].append(child)
        else:
            ne_tree[1].append(process_nested_ne(child))

    return ne_tree


def hierarchy_to_nested_list(hierarchy: list) -> list:
    return [process_nested_ne(ne) for ne in hierarchy]


def convert_folder(json_dir: Path) -> int:
    if not json_dir.exists() or not json_dir.is_dir():
        raise ValueError(f"JSON folder does not exist or is not a directory: {json_dir}")

    converted = 0
    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue

        json_path = json_dir / filename
        with json_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        hierarchy_list = hierarchy_to_nested_list(data["hierarchy"])

        pkl_path = json_path.with_suffix(".pkl")
        with pkl_path.open("wb") as fh:
            pickle.dump(hierarchy_list, fh)

        converted += 1

    return converted


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python json_to_pkl.py <json_dir>")
        print("<json_dir>: Path to directory where the JSON files are stored")
        sys.exit(1)

    json_dir = Path(sys.argv[1])
    converted = convert_folder(json_dir)
    print(f"Converted {converted} .json file(s) to .pkl in {json_dir}.")


if __name__ == "__main__":
    main()
