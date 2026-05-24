"""Parse BIO files."""
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from itertools import pairwise
from operator import attrgetter
from pathlib import Path

PARSE_TOKEN = re.compile(r"(?P<text>[^\s]+) (?P<tag>(I|O|B))(\-(?P<ent>[^\s]+))?")
"""Regex that parses a line of a BIO file"""

_logger = logging.getLogger(__name__)


class Tag(Enum):
    """Supported Beginning-Inside-Outside tags."""

    BEGINNING = "B"
    INSIDE = "I"
    OUTSIDE = "O"


def _make_ner_label(tag: Tag, label: str | None) -> str:
    """Create the corresponding IOB label from the given tag and label.

    Args:
        tag (Tag): Beginning-Inside-Outside tag.
        label (str | None): Label of the token.

    Returns:
        str: Corresponding IOB label.

    Examples:
        >>> _make_ner_label(tag=Tag.BEGINNING, label="GPE")
        'B-GPE'
        >>> _make_ner_label(tag=Tag.INSIDE, label="GPE")
        'I-GPE'
        >>> _make_ner_label(tag=Tag.OUTSIDE, label=None)
        'O'

    """
    if tag == Tag.OUTSIDE:
        assert label is None, f"Invalid label `{label}` with tag `{tag.value}`"
        return tag.value

    assert label, f"No named entity label found with tag `{tag.value}`"

    return f"{tag.value}-{label}"


@dataclass(slots=True)
class Token:
    """Token as tokenized in the BIO document."""

    idx: int
    """Index of the token in the document."""
    text: str
    """Text representation of the token."""
    level: int = field(default_factory=int)
    """Token level"""

    @property
    def _data(self) -> re.Match:
        parsed = PARSE_TOKEN.match(self.text)
        assert parsed is not None, "Could not parse annotation."
        return parsed

    @property
    def word(self) -> str:
        """Text content of the token.

        Examples:
            >>> Token(idx=0, text="Chicken B-Animal").word
            'Chicken'
        """
        return self._data.group("text")

    @property
    def label(self) -> str | None:
        """Named entity type of this token.

        Examples:
            >>> Token(idx=0, text="Chicken B-Animal").label
            'Animal'
        """
        return self._data.group("ent")

    @property
    def tag(self) -> Tag:
        """IOB code of named entity tag.

        Examples:
            >>> Token(idx=0, text="Chicken B-Animal").tag
            <Tag.BEGINNING: 'B'>
        """
        return Tag(self._data.group("tag"))

    @property
    def iob_label(self) -> str:
        """IOB label (Tag + Entity).

        Examples:
            >>> Token(idx=0, text="Chicken B-Animal").iob_label
            'B-Animal'
        """
        return _make_ner_label(tag=self.tag, label=self.label)

    @property
    def char_labels(self) -> list[str]:
        """Character-level IOB labels.

        Examples:
            >>> Token(idx=0, text="Some B-PER").labels
            ['B-PER', 'I-PER', 'I-PER', 'I-PER']

            >>> Token(idx=1, text="one I-PER").labels
            ['I-PER', 'I-PER', 'I-PER'].
        """
        if self.tag == Tag.OUTSIDE:
            return [self.iob_label] * len(self.word)
        return [self.iob_label] + [
            _make_ner_label(tag=Tag.INSIDE, label=self.label),
        ] * (len(self.word) - 1)

    @property
    def chars(self) -> list[str]:
        """The list of characters making up the token.

        Examples:
            >>> Token(idx=0, text="Chicken B-Animal").chars
            ['C', 'h', 'i', 'c', 'k', 'e', 'n']
        """
        return list(self.word)


@dataclass(slots=True)
class Span:
    """Representation of a Named Entity Span."""

    tokens: list[Token] = field(default_factory=list)
    """List of tokens in the Span"""

    @property
    def text(self) -> str:
        """Join every word of the span by a whitespace.

        Examples:
            >>> Span(tokens=[
            ...         Token(idx=0, text="Chicken B-Animal"),
            ...         Token(idx=1, text="run I-Animal")
            ... ]).text
            'Chicken run'
        """
        return " ".join(map(attrgetter("word"), self.tokens))

    @property
    def label(self) -> str | None:
        """The named entity type of this span. All tokens composing the span have the same.

        Examples:
            >>> Span(tokens=[
            ...         Token(idx=0, text="Chicken B-Animal"),
            ...         Token(idx=1, text="run I-Animal")
            ... ]).label
            'Animal'
        """
        if not self.tokens:
            return
        return self.tokens[0].label

    @property
    def idx(self) -> int | None:
        """The index of the first token of the span.

        Examples:
            >>> Span(tokens=[
            ...         Token(idx=0, text="Chicken B-Animal"),
            ...         Token(idx=1, text="run I-Animal")
            ... ]).idx
            0
        """
        if not self.tokens:
            return None
        return self.tokens[0].idx

    @property
    def end(self) -> int | None:
        """The index of the first token after the span.

        Examples:
            >>> Span(tokens=[
            ...         Token(idx=0, text="Chicken B-Animal"),
            ...         Token(idx=1, text="run I-Animal")
            ... ]).end
            2
        """
        if not self.tokens:
            return
        return self.tokens[-1].idx + 1

    def add_token(self, token: Token) -> None:
        """Add the provided token to this span. The token's label must match the Span's.

        Args:
            token (Token): Token to add to this span.
        """
        if self.label:
            assert (
                token.label == self.label
            ), "This token doesn't have the same label as this span."
        self.tokens.append(token)

    @property
    def labels(self) -> list[str]:
        """Character-level IOB labels.

        Examples:
            >>> Span(tokens=[
            ...         Token(idx=0, text="Chicken B-Animal"),
            ...         Token(idx=1, text="run I-Animal")
            ... ]).labels
            ['B-Animal', 'I-Animal', 'I-Animal', 'I-Animal', 'I-Animal', 'I-Animal', 'I-Animal', 'I-Animal', 'I-Animal', 'I-Animal', 'I-Animal']
        """
        if not self.tokens:
            return []

        return [_make_ner_label(tag=Tag.BEGINNING, label=self.label)] + [
            _make_ner_label(tag=Tag.INSIDE, label=self.label),
        ] * (len(self.text) - 1)

    @property
    def chars(self) -> list[str]:
        """Characters making up the span.

        Examples:
            >>> Span(
            ...     tokens=[
            ...             Token(idx=0, text="Chicken B-Animal"),
            ...             Token(idx=1, text="run I-Animal")
            ...     ]
            ... ).chars
            ['C', 'h', 'i', 'c', 'k', 'e', 'n', ' ', 'r', 'u', 'n']
        """
        return list(self.text)

    @property
    def level(self) -> int:
        """Level of the current span.

        Returns:
            int: Level.
        """
        levels = {token.level for token in self.tokens}
        assert (
            len(list(levels)) == 1
        ), f"Inconsistent level for current span {self.tokens}"
        return list(levels)[0]


@dataclass(slots=True)
class Document:
    """Representation of a BIO document."""

    filename: str
    """Document filename"""
    bio_repr: str
    """Full BIO representation of the Document"""
    tokens: list[Token] = field(default_factory=list)
    """List of the tokens in the Document"""

    spans: list[Span] = field(default_factory=list)
    """List of the spans in the Document"""

    def __post_init__(self):
        """Parses the tokens and the entity spans in the document."""
        span: Span | None = None
        for idx, line in enumerate(self.bio_repr.splitlines()):
            try:
                token = Token(idx=idx, text=line)
                self.tokens.append(token)
                # Build spans
                match token.tag:
                    case Tag.OUTSIDE:
                        # Close current span if present
                        if span:
                            self.spans.append(span)
                            span = None
                    case Tag.INSIDE:
                        assert span, f"Found `{Tag.INSIDE}` before `{Tag.BEGINNING}`."
                        span.add_token(token)
                    case Tag.BEGINNING:
                        # Close current span if present
                        if span:
                            self.spans.append(span)
                        # Start new one
                        span = Span()
                        span.add_token(token)
            except AssertionError as e:
                _logger.error(f"Error on token n°{token.idx}: {e}")
                raise Exception from e

        # Last span
        if span and span.tokens:
            self.spans.append(span)

    @property
    def words(self) -> list[str]:
        """List of words making up the document."""
        return list(map(attrgetter("word"), self.tokens))

    @property
    def entities(self) -> list[tuple[str, str]]:
        """List of entities making up the document."""
        return list(
            map(attrgetter("label", "text"), filter(attrgetter("label"), self.spans)),
        )

    @property
    def word_entities(self) -> list[tuple[str, str]]:
        """List of entities in the words making up the document."""
        return list(
            map(attrgetter("label", "word"), filter(attrgetter("label"), self.tokens)),
        )

    @property
    def text(self) -> str:
        """Join every word of the span by a whitespace."""
        return " ".join(map(attrgetter("word"), self.tokens))

    @property
    def char_labels(self) -> list[str]:
        r"""Character-level IOB labels.

        Spaces between two tokens part of the same entities with the same label get the same label, others get 'O'.

        Examples:
            The space between 'I' and 'run' is tagged as 'I-Animal', because it's the same named entity label.
            >>> Document(bio_repr="I B-Animal\nrun I-Animal").char_labels
            ['B-Animal', 'I-Animal', 'I-Animal', 'I-Animal', 'I-Animal']

            The space between 'run' and 'fast' is tagged as 'O', because it's not the same label.
            >>> Document(bio_repr="run B-Animal\nfast O").char_labels
            ['B-Animal', 'I-Animal', 'I-Animal', 'O', 'O', 'O', 'O', 'O']

            The space between 'dog' and 'cat' is tagged as 'O', because it's not the same entity.
            >>> Document(bio_repr="run B-Animal\ncat B-Animal").char_labels
            ['B-Animal', 'I-Animal', 'I-Animal', 'O', 'B-Animal', 'I-Animal', 'I-Animal']
        """
        tags = []
        for token, next_token in pairwise(self.tokens + [None]):
            # Add token tags
            tags.extend(token.char_labels)
            if next_token and (
                token.label == next_token.label and not next_token.tag == Tag.BEGINNING
            ):
                tags.append(next_token.iob_label)
            elif next_token:
                tags.append(Tag.OUTSIDE.value)
        return tags

    @property
    def word_labels(self) -> list[str]:
        r"""Word-level IOB labels.

        Spaces between two tokens with the same label get the same label, others get 'O'.

        Examples:
            The space between 'I' and 'run' is tagged as 'I-Animal', because it's the same named entity label.
            >>> Document(bio_repr="I B-Animal\nrun I-Animal").word_labels
            ['Animal', 'Animal', 'Animal']

            The space between 'run' and 'fast' is tagged as 'O', because it's not the same label.
            >>> Document(bio_repr="run B-Animal\nfast O").word_labels
            ['Animal', 'O', 'O']
        """
        tags = []
        for token, next_token in pairwise(self.tokens + [None]):
            # Add token tags
            tags.append(token.label or Tag.OUTSIDE.value)

            # Token of the next space
            if (
                # This is not the last token
                next_token
                # This token is not tagged as O
                and token.tag != Tag.OUTSIDE
                # Same label between consecutive tokens
                and token.label == next_token.label
            ):
                tags.append(token.label)
            elif next_token:
                tags.append(Tag.OUTSIDE.value)
        return tags

    @property
    def chars(self) -> list[str]:
        r"""Characters making up the token.

        Examples:
            >>> Document(bio_repr="I B-Animal\nrun I-Animal").chars
            ['I', ' ', 'r', 'u', 'n']
        """
        return list(self.text)

    @classmethod
    def from_file(cls, filepath: Path) -> "Document":
        """Load a Document from a IOB file.

        Args:
            filepath (Path): Path to the file to load.

        Returns:
            Document: Parsed document
        """
        return Document(filepath.stem, filepath.read_text())
