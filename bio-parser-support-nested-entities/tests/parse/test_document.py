import pytest
from bio_parser.parse.document import Document, Span, Tag, Token, _make_ner_label

from tests.parse import DATA_DIR

FILEPATH = DATA_DIR / "valid.bio"


@pytest.fixture()
def document() -> Document:
    return Document.from_file(FILEPATH)


@pytest.mark.parametrize(
    ("tag", "label", "output"),
    [
        (Tag.OUTSIDE, None, "O"),
        (Tag.BEGINNING, "GPE", "B-GPE"),
        (Tag.INSIDE, "GPE", "I-GPE"),
    ],
)
def test_make_ner_label(tag: Tag, label: str, output: str):
    assert _make_ner_label(tag=tag, label=label) == output


@pytest.mark.parametrize(
    ("tag", "label", "error"),
    [
        (Tag.OUTSIDE, "GPE", "Invalid label `GPE` with tag `O`"),
        (Tag.BEGINNING, None, "No named entity label found with tag `B`"),
        (Tag.INSIDE, None, "No named entity label found with tag `I`"),
    ],
)
def test_make_ner_label_invalid(tag: Tag, label: str, error: str):
    with pytest.raises(AssertionError, match=error):
        _ = _make_ner_label(tag=tag, label=label)


def test_parse_document(document: Document):
    # Check words
    assert document.words == [
        "San",
        "Francisco",
        "considers",
        "banning",
        "sidewalk",
        "delivery",
        "robots",
    ]

    # Check entities
    assert document.entities == [
        ("GPE", "San Francisco"),
        ("VERB", "banning"),
    ]

    # Check word entities
    assert document.word_entities == [
        ("GPE", "San"),
        ("GPE", "Francisco"),
        ("VERB", "banning"),
    ]

    # Check text
    assert document.text == "San Francisco considers banning sidewalk delivery robots"

    # Check labels
    assert document.char_labels == ["B-GPE"] + ["I-GPE"] * len("an Francisco") + [
        "O"
    ] * len(" considers ") + ["B-VERB"] + ["I-VERB"] * len("anning") + ["O"] * len(
        " sidewalk delivery robots"
    )
    assert document.word_labels == [
        "GPE",
        "GPE",
        "GPE",
        "O",
        "O",
        "O",
        "VERB",
        "O",
        "O",
        "O",
        "O",
        "O",
        "O",
    ]

    # Check chars
    assert document.chars == list(
        "San Francisco considers banning sidewalk delivery robots"
    )


def test_parse_span(document: Document):
    span: Span = document.spans[0]

    # Check text
    assert span.text == "San Francisco"

    # Check label
    assert span.label == "GPE"

    # Check idx
    assert span.idx == 0

    # Check end
    assert span.end == 2

    # Check chars
    assert span.chars == list("San Francisco")

    # Check labels
    assert span.labels == ["B-GPE"] + ["I-GPE"] * len("an Francisco")


def test_parse_token(document: Document):
    # B- token
    token: Token = document.spans[0].tokens[0]

    # Check word
    assert token.word == "San"

    # Check label
    assert token.label == "GPE"

    # Check label
    assert token.tag == Tag.BEGINNING

    # Check IOB Label
    assert token.iob_label == "B-GPE"

    # Check labels
    assert token.char_labels == ["B-GPE", "I-GPE", "I-GPE"]

    # Check chars
    assert token.chars == ["S", "a", "n"]

    # I- token
    token: Token = document.spans[0].tokens[1]

    # Check word
    assert token.word == "Francisco"

    # Check label
    assert token.label == "GPE"

    # Check label
    assert token.tag == Tag.INSIDE

    # Check IOB Label
    assert token.iob_label == "I-GPE"

    # Check labels
    assert token.char_labels == [
        "I-GPE",
        "I-GPE",
        "I-GPE",
        "I-GPE",
        "I-GPE",
        "I-GPE",
        "I-GPE",
        "I-GPE",
        "I-GPE",
    ]

    # Check chars
    assert token.chars == ["F", "r", "a", "n", "c", "i", "s", "c", "o"]

    # O token
    token: Token = document.tokens[-1]

    # Check word
    assert token.word == "robots"

    # Check label
    assert token.label is None

    # Check label
    assert token.tag == Tag.OUTSIDE

    # Check IOB Label
    assert token.iob_label == "O"

    # Check labels
    assert token.char_labels == ["O", "O", "O", "O", "O", "O"]

    # Check chars
    assert token.chars == ["r", "o", "b", "o", "t", "s"]


def test_consecutive_entities():
    # BIO FILE
    # dog B-Animal
    # cat B-Animal
    document = Document("test", "dog B-Animal\ncat B-Animal")

    assert document.chars == ["d", "o", "g", " ", "c", "a", "t"]

    assert document.char_labels == [
        "B-Animal",
        "I-Animal",
        "I-Animal",
        "O",  # Character between two new entities should be set to O
        "B-Animal",
        "I-Animal",
        "I-Animal",
    ]


@pytest.mark.parametrize(
    "annotation",
    ["Something something", "Something A-GPE", "Something GPE-A", "Something A"],
)
def test_invalid_token(annotation: str):
    with pytest.raises(AssertionError, match="Could not parse annotation"):
        _ = Token(idx=0, text=annotation).word
