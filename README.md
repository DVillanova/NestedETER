## Nested ETER

Nested Entity Token Error Rate (ETER) metrics with support for **micro/macro**
averaging and **ordered/unordered** matching, plus an end-to-end pipeline that
goes from BIO files all the way to a timed evaluation report.

### Installation

The repository is self-contained: it bundles both the `nested-eter`
package (this repo) and the patched `bio-parser` (under
`bio-parser-support-nested-entities/`) that supports nested entities.
Two equally valid setups are provided.

#### Option A — auto-provisioned virtualenv (recommended)

You don't have to install anything by hand. The first run of
`run_pipeline.sh` will:

1. Create a local virtual environment in `.venv/`.
2. Install `nested-eter` and `bio-parser` in editable mode from
   `requirements.txt`.
3. Activate it for the rest of the run.

Subsequent runs reuse the existing `.venv/` and start immediately. Only
prerequisite: **Python 3.10** or later with the `venv` module
(`sudo apt install python3.10-venv` on Debian/Ubuntu).

If you already manage your own environment, just `pip install -r
requirements.txt` and pass `SKIP_VENV=1` to `run_pipeline.sh`.

#### Option B — Docker image

For fully reproducible runs without touching the host Python, build the
image once and let the wrapper script handle bind-mounts and rebuilds.
The image is based on **Python 3.10-slim** and requires no local Python
installation:

```bash
./docker_run.sh              # builds the image on first use, then runs
./docker_run.sh --rebuild    # force-rebuild after editing the code
```

Manual equivalent:

```bash
docker build -t nested-eter .
docker run --rm \
    -v "$PWD/hypotheses:/data/hypotheses" \
    -v "$PWD/labels:/data/labels" \
    -v "$PWD/char_hypotheses:/data/char_hypotheses" \
    -v "$PWD/char_labels:/data/char_labels" \
    -v "$PWD:/data/report" \
    nested-eter
```

Either route exposes the same two CLIs internally:

- `compute-eter` — computes Nested ETER over a pair of `.pkl` corpora.
- `bio-parser`   — validates `.bio` files and emits sibling `.json` files.

### End-to-end pipeline

Populate the two input folders with word-level BIO files:

```
hypotheses/    # *.bio  - system predictions (word-level)
labels/        # *.bio  - ground truth       (word-level)
```

Then run either:

```bash
./run_pipeline.sh        # native virtualenv flow (Option A)
./docker_run.sh          # Docker flow             (Option B)
```

This will:

1. Synchronise filenames across `hypotheses/` and `labels/` (creates a
   one-token dummy `.bio` where a file is missing on one side, via
   `fix_bio_folders.py`).
2. Generate char-level BIO files into `char_hypotheses/` and `char_labels/`
   using `word_to_char_bio.py`.
3. Parse every `.bio` into a sibling `.json` using `bio-parser validate
   --allow-nested` for all four folders.
4. Convert every `.json` into a sibling `.pkl` using `json_to_pkl.py` for all
   four folders.
5. Run the full ETER evaluation (`time_measurement_evaluation.sh`), producing
   `evaluation_report.txt` with macro/micro and ordered/unordered scores at
   both word and char level, including per-call timings.

After the run, each of `hypotheses/`, `labels/`, `char_hypotheses/` and
`char_labels/` contains the original `.bio` files alongside generated
`.json` and `.pkl` files with matching base names. Each tool only operates
on files with its own extension, so the artefacts can safely coexist.

Override default folder locations via environment variables:

```bash
HYP_DIR=preds LABELS_DIR=gt ./run_pipeline.sh
```

### Manual CLI usage

If you prefer to drive the steps individually:

```bash
# Validate BIO files (writes <name>.json next to each <name>.bio)
bio-parser validate --allow-nested labels/*.bio

# Convert JSON hierarchies to PKL (filters .json automatically)
python json_to_pkl.py labels/

# Compute one ETER metric
compute-eter <macro|micro> <ordered|unordered> <ref_dir> <hyp_dir>
```

- **`<macro|micro>`**: whether to macro-average or micro-average the ETER score.
- **`<ordered|unordered>`**: whether to enforce reading-order constraints
  (`ordered`) or use the Hungarian algorithm (`unordered`).
- **`<ref_dir>`** / **`<hyp_dir>`**: directories containing the reference /
  hypothesis `.pkl` files (other extensions are ignored).

The command prints the raw score, a rounded score and a 95 % confidence
interval.

### Programmatic usage

You can also import the main metrics directly:

```python
from nested_eter import (
    compute_micro_eter,
    compute_macro_eter,
    compute_micro_ordered_eter,
    compute_macro_ordered_eter,
)
```

Each function accepts two arguments — `list_ref_docs` and `list_hyp_docs` —
and returns a `(score, standard_error)` tuple in percentage units.

#### Named-entity tree encoding

Each `.pkl` file contains one document represented as a **list of
named-entity (NE) trees**, one entry per entity span in the document.
An NE tree is a two-element list:

```
[category, children]
```

- **`category`** (`str`) — the entity type label (e.g. `"persName"`,
  `"placeName"`, `"date"`).
- **`children`** (`list`) — the tokens that make up the entity span.
  Each element is either:
  - a `str` — a leaf token, or
  - another `[category, children]` list — a **nested entity** embedded
    inside the outer span.

A document with no entities is an empty list `[]`.

##### Flat entity (single token)

```python
["persName", ["Johannes"]]
```

##### Flat entity (multiple tokens)

From `labels/CG-L_219.r1.bio`:

```python
["persName", ["Waniek,", "bratrzie", "z", "Nespeczowa"]]
```

##### Nested entity

A `persName` that contains an embedded `roleName`:

```python
["persName", [
    "Waniek",
    ["roleName", ["regis", "Bohemie"]],
    "z",
    "Nespeczowa"
]]
```

##### Full document example

A complete document (list of NE trees) as loaded from a `.pkl` file:

```python
[
    ["placeName", ["Boemie"]],
    ["placeName", ["Polonie"]],
    ["persName",  ["Waniek,", "bratrzie", "z", "Nespeczowa"]],
    ["date",      ["nach", "Crists", "geburte"]],
]
```

This is exactly the structure returned by `pickle.load()` on any `.pkl`
file produced by the pipeline, and the structure expected by all four
metric functions.
