## Nested ETER

Nested Entity Token Error Rate (ETER) metrics with support for **micro/macro** averaging and **ordered/unordered** matching.

### Installation

Install from PyPI (once published) with:

```bash
pip install nested-eter
```

This will install the library and expose the `compute-eter` command-line tool.

### CLI usage

The CLI mirrors the original script interface:

```bash
compute-eter <macro|micro> <ordered|unordered> <ref_dir> <hyp_dir>
```

- **`<macro|micro>`**: whether to macro-average or micro-average the ETER score.  
- **`<ordered|unordered>`**: whether to enforce reading-order constraints (`ordered`) or use the Hungarian algorithm (`unordered`).  
- **`<ref_dir>`**: directory containing the reference `.pkl` files.  
- **`<hyp_dir>`**: directory containing the hypothesis `.pkl` files.

The command prints the raw score, a rounded score, and a 95% confidence interval.

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

Each function operates on lists of named-entity trees for reference and hypothesis corpora and returns a tuple of `(score, standard_error)` in percentage units.

