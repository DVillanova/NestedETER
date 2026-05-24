import pytest
from bio_parser.parse.document import Tag
from bio_parser.parse.nested_document import NestedDocument, NestedToken

from tests.parse import DATA_DIR

FILEPATH = DATA_DIR / "valid_nested.bio"


@pytest.fixture()
def nested_document() -> NestedDocument:
    return NestedDocument.from_file(FILEPATH)


def test_parse_document(nested_document: NestedDocument):
    # Check words
    assert nested_document.words == [
        "Charles",
        "né",
        "à",
        "Beaune",
        "en",
        "1836",
        "père",
        "Jean",
        "Bigre",
        "charpentier",
        "de",
        "cette",
        "paroisse",
        "mère",
        "Marie",
    ]

    # Check entities
    assert nested_document.entities == [
        ("child", "Charles né à Beaune en 1836"),
        ("name", "Charles"),
        ("location", "Beaune"),
        ("date", "1836"),
        ("father", "Jean Bigre charpentier de cette paroisse"),
        ("name", "Jean"),
        ("surname", "Bigre"),
        ("occupation", "charpentier"),
        ("location", "cette paroisse"),
        ("mother", "Marie"),
        ("name", "Marie"),
    ]

    # Check word entities
    assert nested_document.word_entities == [
        (["child", "name"], "Charles"),
        (["child"], "né"),
        (["child"], "à"),
        (["child", "location"], "Beaune"),
        (["child"], "en"),
        (["child", "date"], "1836"),
        (["father", "name"], "Jean"),
        (["father", "surname"], "Bigre"),
        (["father", "occupation"], "charpentier"),
        (["father"], "de"),
        (["father", "location"], "cette"),
        (["father", "location"], "paroisse"),
        (["mother", "name"], "Marie"),
    ]

    # Check text
    assert (
        nested_document.text
        == "Charles né à Beaune en 1836 père Jean Bigre charpentier de cette paroisse mère Marie"
    )

    # Check chars
    assert nested_document.chars == list(
        "Charles né à Beaune en 1836 père Jean Bigre charpentier de cette paroisse mère Marie"
    )


def test_parse_nested_token(nested_document: NestedDocument):
    nested_token: NestedToken = nested_document.nested_tokens[0]

    # Check word
    assert nested_token.word == "Charles"

    # Check label
    assert nested_token.labels == ["child", "name"]

    # Check label
    assert nested_token.tags == [Tag.BEGINNING, Tag.BEGINNING]

    # Check IOB Label
    assert nested_token.iob_labels == ["B-child", "B-name"]

    # Check labels
    assert nested_token.char_labels == [
        ["B-child", "I-child", "I-child", "I-child", "I-child", "I-child", "I-child"],
        ["B-name", "I-name", "I-name", "I-name", "I-name", "I-name", "I-name"],
    ]

    # Check chars
    assert nested_token.chars == ["C", "h", "a", "r", "l", "e", "s"]

    # I- token
    nested_token: NestedToken = nested_document.nested_tokens[3]

    # Check word
    assert nested_token.word == "Beaune"

    # Check label
    assert nested_token.labels == ["child", "location"]

    # Check label
    assert nested_token.tags == [Tag.INSIDE, Tag.BEGINNING]

    # Check IOB Label
    assert nested_token.iob_labels == ["I-child", "B-location"]

    # Check labels
    assert nested_token.char_labels == [
        ["I-child", "I-child", "I-child", "I-child", "I-child", "I-child"],
        [
            "B-location",
            "I-location",
            "I-location",
            "I-location",
            "I-location",
            "I-location",
        ],
    ]

    # Check chars
    assert nested_token.chars == ["B", "e", "a", "u", "n", "e"]

    # O token
    nested_token: NestedToken = nested_document.nested_tokens[-2]

    # Check word
    assert nested_token.word == "mère"

    # Check label
    assert nested_token.labels == [None]

    # Check label
    assert nested_token.tags == [Tag.OUTSIDE]

    # Check IOB Label
    assert nested_token.iob_labels == ["O"]

    # Check labels
    assert nested_token.char_labels == [["O", "O", "O", "O"]]

    # Check chars
    assert nested_token.chars == ["m", "è", "r", "e"]
