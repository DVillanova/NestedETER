"""Parse nested BIO files."""
import logging
import re
from dataclasses import dataclass, field
from operator import attrgetter
from pathlib import Path
from typing import Any

from bio_parser.parse.document import Span, Tag, Token

PARSE_BIO_LINE = re.compile(
    r"(?P<text>[^\s]+)\s+(?P<labels>(?:[^\s]+(?:\-[^\s]+)?\s*)+)"
)

"""Regex that parses a line of a BIO file"""

_logger = logging.getLogger(__name__)


@dataclass(slots=True)
class NestedToken:
    """Token as tokenized in the BIO document, that may contain multiple labels."""

    idx: int
    """Index of the nested token in the document."""
    text: str
    """Text representation of the nested token."""

    @property
    def _data(self) -> list[str]:
        """Nested BIO line parsing."""
        parsed_global = PARSE_BIO_LINE.match(self.text)
        text = parsed_global.group("text")
        labels = list(parsed_global.group("labels").strip().split(" "))
        return [f"{text} {label}" for label in labels]

    @property
    def tokens(self) -> list[Token]:
        """List of flat tokens associated to the nested token.

        Examples:
            >>> NestedToken(idx=0, text="Jean B-child B-name").tokens
            [Token(idx=0, text='Jean B-child'), Token(idx=0, text='Jean B-name')]
        """
        return [
            Token(idx=self.idx, text=text_repr, level=i)
            for i, text_repr in enumerate(self._data)
        ]

    @property
    def word(self) -> str:
        """Text content of the nested token.

        Examples:
            >>> NestedToken(idx=0, text="Jean B-child B-name").word
            'Jean'
        """
        return self.tokens[0].word

    @property
    def labels(self) -> list[str | None]:
        """Named entity type of this token.

        Examples:
            >>> NestedToken(idx=0, text="Jean B-child B-name").label
            ["child", "name"]
        """
        return [token.label for token in self.tokens]

    @property
    def tags(self) -> list[Tag]:
        """IOB tags of named entity tag.

        Examples:
            >>> NestedToken(idx=0, text="Jean B-child B-name").tags
            [<Tag.BEGINNING: 'B'>, <Tag.BEGINNING: 'B'>]
        """
        return [token.tag for token in self.tokens]

    @property
    def iob_labels(self) -> list[str]:
        """IOB label (Tag + Entity).

        Examples:
            >>> NestedToken(idx=0, text="Jean B-child B-name").iob_label
            ['B-child', 'B-name']
        """
        return [token.iob_label for token in self.tokens]

    @property
    def char_labels(self) -> list[list[str]]:
        """Character-level IOB labels.

        Examples:
            >>> NestedToken(idx=0, text="Jean B-child B-name").char_labels
            [['B-child', 'I-child', 'I-child', 'I-child'], ['B-name', 'I-name', 'I-name', 'I-name']]
        """
        return [token.char_labels for token in self.tokens]

    @property
    def chars(self) -> list[str]:
        """The list of characters making up the token.

        Examples:
            >>> NestedToken(idx=0, text="Jean B-child B-name").chars
            ['J', 'e', 'a', 'n']
        """
        return self.tokens[0].chars


@dataclass(slots=True)
class NestedSpan:
    """Representation of a Nested Named Entity Span."""

    spans: list[Span] = field(default_factory=list)
    """List of Span in the NestedSpan"""

    @property
    def hierarchy(self) -> str:
        """Build a hierarchy of Spans.

        Examples:
            >>> NestedSpan(spans=[
            ...     Span(tokens=[
            ...         Token(idx=0, text='Bolke, B-persName', level=0),
            ...         Token(idx=1, text='herczog I-persName', level=0),
            ...         Token(idx=2, text='von I-persName', level=0),
            ...         Token(idx=3, text='Slezien I-persName', level=0),
            ...         Token(idx=4, text='und I-persName', level=0),
            ...         Token(idx=5, text='herre I-persName', level=0),
            ...         Token(idx=6, text='czu I-persName', level=0),
            ...         Token(idx=7, text='Furstemberg I-persName', level=0)
            ...     ]),
            ...     Span(tokens=[Token(idx=3, text='Slezien B-placeName', level=1), Token(idx=4, text='und I-placeName', level=1)]),
            ...     Span(tokens=[Token(idx=3, text='Slezien B-FakeEntity', level=2)]),
            ...     Span(tokens=[Token(idx=7, text='Furstemberg B-placeName', level=1)])
            ... ]).hierarchy
                {
                    "category":"persName",
                    "children":[
                        "Bolke",
                        "herczog",
                        "von",
                        {
                            "category":"placeName",
                            "children":[
                                {
                                "category":"FakeEntity",
                                "children":[
                                    "Slezien"
                                ]
                                }
                            ]
                        },
                        "und",
                        "herre",
                        "czu",
                        {
                            "category":"placeName",
                            "children":[
                                "Furstemberg"
                            ]
                        }
                    ]
                }
        """

        # Recursive function to construct the hierarchy
        def build_hierarchy(span):
            # Initialize the base dictionary
            span_dict = {"category": span.label, "children": []}

            for token in span.tokens:
                # Check if a child span starts at this token index
                child_span = next(
                    (
                        s
                        for s in self.spans
                        if s.level > span.level and s.tokens[0].idx == token.idx
                    ),
                    None,
                )
                if child_span:
                    # Add the child span as a nested dictionary
                    span_dict["children"].append(build_hierarchy(child_span))
                else:
                    # Add the token text if no child span exists
                    span_dict["children"].append(
                        token.text.split(" ")[0]
                    )  # Extract the actual word

            return span_dict

        top_level_span = min(self.spans, key=lambda s: s.level)
        return build_hierarchy(top_level_span)


@dataclass(slots=True)
class NestedDocument:
    """Representation of a BIO document."""

    filename: str
    """Document filename"""

    bio_repr: str
    """Full BIO representation of the Document"""

    nested_tokens: list[NestedToken] = field(default_factory=list)
    """List of the nested tokens in the Document"""

    nested_spans: list[NestedSpan] = field(default_factory=list)
    """List of the nested spans in the Document"""

    hierarchy: list[dict[str, Any]] = field(default_factory=list)
    """Hierarchy required for metrics"""

    def __post_init__(self):
        """Parses the tokens and the entity spans in the document."""
        # Build nested spans with hierarchy
        self.nested_spans = self._build_nested_spans()

        # Build JSON hierarchy
        self.hierarchy = self._build_hierarchy()

    def _build_nested_spans(self) -> list[dict[str, Span | list[Span]]]:
        """Build span hierarchy based on token position in the BIO file."""

        def is_inside(span, parent_span):
            return (
                (span.idx >= parent_span.idx)
                and (span.end <= parent_span.end)
                and (parent_span != span)
            )

        flat_spans = self._build_spans()
        nested_spans = []
        parents = [span for span in flat_spans if span.level == 0]
        for parent in parents:
            children = [
                span
                for span in flat_spans
                if is_inside(span, parent) and parent.level < span.level
            ]
            nested_spans.append(NestedSpan([parent] + children))
        return nested_spans

    def _build_hierarchy(self) -> list[dict]:
        return [nested_span.hierarchy for nested_span in self.nested_spans]

    def _build_spans(self):
        """Build spans."""
        spans = []
        current_spans: dict[str, Span] = {}  # Keep track of current spans by category
        for idx, line in enumerate(self.bio_repr.splitlines()):
            try:
                nested_token = NestedToken(idx=idx, text=line)
                self.nested_tokens.append(nested_token)

                for _idx, token in enumerate(nested_token.tokens):
                    # Build spans
                    match token.tag:
                        case Tag.OUTSIDE:
                            # Close all current spans
                            for span in current_spans.values():
                                spans.append(span)
                            current_spans = {}

                        case Tag.INSIDE:
                            assert (
                                token.label in current_spans
                            ), f"Found `{Tag.INSIDE}` before `{Tag.BEGINNING}`."
                            # Continue current span
                            current_spans[token.label].add_token(token)

                        case Tag.BEGINNING:
                            # End existing span if necessary
                            if token.label in current_spans:
                                span = current_spans.pop(token.label)
                                spans.append(span)

                            # Start a new span
                            current_spans[token.label] = Span()
                            current_spans[token.label].add_token(token)

            except AssertionError as e:
                _logger.error(f"Error on token n°{token.idx}: {e}")
                raise Exception from e

        # Last spans
        for span in current_spans.values():
            spans.append(span)
        return spans

    @property
    def words(self) -> list[str]:
        """List of words making up the document."""
        return list(map(attrgetter("word"), self.nested_tokens))

    @property
    def entities(self) -> list[tuple[str, str]]:
        """List of entities making up the document."""
        return list(
            map(
                attrgetter("label", "text"),
                filter(
                    attrgetter("label"),
                    [
                        span
                        for nested_span in self.nested_spans
                        for span in nested_span.spans
                    ],
                ),
            ),
        )

    @property
    def word_entities(self) -> list[tuple[str, str]]:
        """List of entities in the words making up the document."""
        return list(
            map(
                attrgetter("labels", "word"),
                filter(lambda x: x.labels[0] is not None, self.nested_tokens),
            ),
        )

    @property
    def text(self) -> str:
        """Join every word of the span by a whitespace."""
        return " ".join(map(attrgetter("word"), self.nested_tokens))

    @property
    def chars(self) -> list[str]:
        r"""Characters making up the token.

        Examples:
            >>> Document(bio_repr="I B-Animal\nrun I-Animal").chars
            ['I', ' ', 'r', 'u', 'n']
        """
        return list(self.text)

    @classmethod
    def from_file(cls, filepath: Path) -> "NestedDocument":
        """Load a Document from a IOB file.

        Args:
            filepath (Path): Path to the file to load.

        Returns:
            Document: Parsed document
        """
        return NestedDocument(filepath.stem, filepath.read_text())
