import json

from bio_parser.parse.validate import run as validate

from tests.parse import DATA_DIR


def test_valid():
    filepath = DATA_DIR / "valid.bio"
    validate([filepath])

    # A JSON file should have been generated
    output = filepath.with_suffix(".json")
    assert output.exists()

    # Check content of JSON
    assert json.loads(output.read_text()) == {
        "filename": "valid",
        "bio_repr": "San B-GPE\nFrancisco I-GPE\nconsiders O\nbanning B-VERB\nsidewalk O\ndelivery O\nrobots O",
        "tokens": [
            {"idx": 0, "text": "San B-GPE", "level": 0},
            {"idx": 1, "text": "Francisco I-GPE", "level": 0},
            {"idx": 2, "text": "considers O", "level": 0},
            {"idx": 3, "text": "banning B-VERB", "level": 0},
            {"idx": 4, "text": "sidewalk O", "level": 0},
            {"idx": 5, "text": "delivery O", "level": 0},
            {"idx": 6, "text": "robots O", "level": 0},
        ],
        "spans": [
            {
                "tokens": [
                    {"idx": 0, "text": "San B-GPE", "level": 0},
                    {"idx": 1, "text": "Francisco I-GPE", "level": 0},
                ]
            },
            {"tokens": [{"idx": 3, "text": "banning B-VERB", "level": 0}]},
        ],
    }

    # Cleanup
    output.unlink()


def test_valid_nested():
    filepath = DATA_DIR / "valid_nested.bio"

    validate([filepath], allow_nested=True)

    # A JSON file should have been generated
    output = filepath.with_suffix(".json")
    assert output.exists()

    # Check content of JSON
    assert json.loads(output.read_text()) == {
        "filename": "valid_nested",
        "bio_repr": "Charles B-child B-name\nné I-child\nà I-child\nBeaune I-child B-location\nen I-child\n1836 I-child B-date\npère O\nJean B-father B-name\nBigre I-father B-surname\ncharpentier I-father B-occupation\nde I-father\ncette I-father B-location\nparoisse I-father I-location\nmère O\nMarie B-mother B-name\n",
        "nested_tokens": [
            {"idx": 0, "text": "Charles B-child B-name"},
            {"idx": 1, "text": "né I-child"},
            {"idx": 2, "text": "à I-child"},
            {"idx": 3, "text": "Beaune I-child B-location"},
            {"idx": 4, "text": "en I-child"},
            {"idx": 5, "text": "1836 I-child B-date"},
            {"idx": 6, "text": "père O"},
            {"idx": 7, "text": "Jean B-father B-name"},
            {"idx": 8, "text": "Bigre I-father B-surname"},
            {"idx": 9, "text": "charpentier I-father B-occupation"},
            {"idx": 10, "text": "de I-father"},
            {"idx": 11, "text": "cette I-father B-location"},
            {"idx": 12, "text": "paroisse I-father I-location"},
            {"idx": 13, "text": "mère O"},
            {"idx": 14, "text": "Marie B-mother B-name"},
        ],
        "nested_spans": [
            {
                "spans": [
                    {
                        "tokens": [
                            {"idx": 0, "text": "Charles B-child", "level": 0},
                            {"idx": 1, "text": "né I-child", "level": 0},
                            {"idx": 2, "text": "à I-child", "level": 0},
                            {"idx": 3, "text": "Beaune I-child", "level": 0},
                            {"idx": 4, "text": "en I-child", "level": 0},
                            {"idx": 5, "text": "1836 I-child", "level": 0},
                        ]
                    },
                    {"tokens": [{"idx": 0, "text": "Charles B-name", "level": 1}]},
                    {"tokens": [{"idx": 3, "text": "Beaune B-location", "level": 1}]},
                    {"tokens": [{"idx": 5, "text": "1836 B-date", "level": 1}]},
                ]
            },
            {
                "spans": [
                    {
                        "tokens": [
                            {"idx": 7, "text": "Jean B-father", "level": 0},
                            {"idx": 8, "text": "Bigre I-father", "level": 0},
                            {"idx": 9, "text": "charpentier I-father", "level": 0},
                            {"idx": 10, "text": "de I-father", "level": 0},
                            {"idx": 11, "text": "cette I-father", "level": 0},
                            {"idx": 12, "text": "paroisse I-father", "level": 0},
                        ]
                    },
                    {"tokens": [{"idx": 7, "text": "Jean B-name", "level": 1}]},
                    {"tokens": [{"idx": 8, "text": "Bigre B-surname", "level": 1}]},
                    {
                        "tokens": [
                            {"idx": 9, "text": "charpentier B-occupation", "level": 1}
                        ]
                    },
                    {
                        "tokens": [
                            {"idx": 11, "text": "cette B-location", "level": 1},
                            {"idx": 12, "text": "paroisse I-location", "level": 1},
                        ]
                    },
                ]
            },
            {
                "spans": [
                    {"tokens": [{"idx": 14, "text": "Marie B-mother", "level": 0}]},
                    {"tokens": [{"idx": 14, "text": "Marie B-name", "level": 1}]},
                ]
            },
        ],
        "hierarchy": [
            {
                "category": "child",
                "children": [
                    {"category": "name", "children": ["Charles"]},
                    "né",
                    "à",
                    {"category": "location", "children": ["Beaune"]},
                    "en",
                    {"category": "date", "children": ["1836"]},
                ],
            },
            {
                "category": "father",
                "children": [
                    {"category": "name", "children": ["Jean"]},
                    {"category": "surname", "children": ["Bigre"]},
                    {"category": "occupation", "children": ["charpentier"]},
                    "de",
                    {"category": "location", "children": ["cette", "paroisse"]},
                ],
            },
            {
                "category": "mother",
                "children": [{"category": "name", "children": ["Marie"]}],
            },
        ],
    }

    # Cleanup
    output.unlink()


def test_valid_not_nested():
    filepath = DATA_DIR / "valid_nested.bio"

    validate([filepath], allow_nested=False)

    # A JSON file should have been generated
    output = filepath.with_suffix(".json")
    assert output.exists()

    # Check content of JSON
    assert json.loads(output.read_text()) == {
        "filename": "valid_nested",
        "bio_repr": "Charles B-child B-name\nné I-child\nà I-child\nBeaune I-child B-location\nen I-child\n1836 I-child B-date\npère O\nJean B-father B-name\nBigre I-father B-surname\ncharpentier I-father B-occupation\nde I-father\ncette I-father B-location\nparoisse I-father I-location\nmère O\nMarie B-mother B-name\n",
        "tokens": [
            {"idx": 0, "text": "Charles B-child B-name", "level": 0},
            {"idx": 1, "text": "né I-child", "level": 0},
            {"idx": 2, "text": "à I-child", "level": 0},
            {"idx": 3, "text": "Beaune I-child B-location", "level": 0},
            {"idx": 4, "text": "en I-child", "level": 0},
            {"idx": 5, "text": "1836 I-child B-date", "level": 0},
            {"idx": 6, "text": "père O", "level": 0},
            {"idx": 7, "text": "Jean B-father B-name", "level": 0},
            {"idx": 8, "text": "Bigre I-father B-surname", "level": 0},
            {"idx": 9, "text": "charpentier I-father B-occupation", "level": 0},
            {"idx": 10, "text": "de I-father", "level": 0},
            {"idx": 11, "text": "cette I-father B-location", "level": 0},
            {"idx": 12, "text": "paroisse I-father I-location", "level": 0},
            {"idx": 13, "text": "mère O", "level": 0},
            {"idx": 14, "text": "Marie B-mother B-name", "level": 0},
        ],
        "spans": [
            {
                "tokens": [
                    {"idx": 0, "text": "Charles B-child B-name", "level": 0},
                    {"idx": 1, "text": "né I-child", "level": 0},
                    {"idx": 2, "text": "à I-child", "level": 0},
                    {"idx": 3, "text": "Beaune I-child B-location", "level": 0},
                    {"idx": 4, "text": "en I-child", "level": 0},
                    {"idx": 5, "text": "1836 I-child B-date", "level": 0},
                ]
            },
            {
                "tokens": [
                    {"idx": 7, "text": "Jean B-father B-name", "level": 0},
                    {"idx": 8, "text": "Bigre I-father B-surname", "level": 0},
                    {"idx": 9, "text": "charpentier I-father B-occupation", "level": 0},
                    {"idx": 10, "text": "de I-father", "level": 0},
                    {"idx": 11, "text": "cette I-father B-location", "level": 0},
                    {"idx": 12, "text": "paroisse I-father I-location", "level": 0},
                ]
            },
            {"tokens": [{"idx": 14, "text": "Marie B-mother B-name", "level": 0}]},
        ],
    }

    # Cleanup
    output.unlink()
