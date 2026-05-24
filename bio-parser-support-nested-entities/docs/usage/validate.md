# Validation

Use the `bio-parser validate` command to parse and validate the structure of one or more BIO2 files.

## Supported format

The BIO2 format is a common tagging format in NER (Named entities recognition) tasks. More details about it on [Wikipedia](https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging)).

An example of such a tagging format is given below.
```plaintext
Alex B-PER
is O
going O
to O
Los B-LOC
Angeles I-LOC
in O
California B-LOC
```

## Usage

You can specify one or more paths to your BIO files. The extension used has to be `.bio`.
The parser will check them one by one and report the first error encountered.

```shell
$ bio-parser validate input.bio
[12:37:20] INFO     Parsing file @ `input.bio`                                                                                            validate.py:19
           INFO     The file @ `input.bio` is valid!                                                                                      validate.py:25
```

With multiple files:
```shell
$ bio-parser validate input1.bio input2.bio
[12:37:20] INFO     Parsing file @ `input1.bio`                                                                                            validate.py:19
           INFO     The file @ `input1.bio` is valid!                                                                                      validate.py:25
[12:37:20] INFO     Parsing file @ `input2.bio`                                                                                            validate.py:19
           INFO     The file @ `input2.bio` is valid!                                                                                      validate.py:25
```

With an invalid file.
```shell
$ bio-parser validate invalid.bio
[12:41:16] INFO     Parsing file @ `invalid.bio`                                                                                                               validate.py:19
           ERROR    Error on token n°0: Found `Tag.INSIDE` before `Tag.BEGINNING`.                                                                            document.py:283
           ERROR    Could not load the file @ `invalid.bio`:                                                                                                   validate.py:24
           INFO     The file @ `invalid.bio` is valid!                                                                                                         validate.py:25
```

In addition to validating the structure of the file, a JSON representation of the BIO file is also saved at the same location.

This JSON file has three keys:

- `bio_repr`: The string in BIO format passed to the command,
- `tokens`: the list of tokens in the file, with their index and text,
- `spans`: the list of NER entities found and their tokens.
