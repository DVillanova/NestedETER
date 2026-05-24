# Development

`bio-parser` uses different tools during its development. You can install needed dependencies using

```shell
pip install pre-commit tox
```

## Contributing

Found an issue that you want to work on? You can create a new branch from `master` to develop. The name should be somewhat related to the issue.

```shell
# Make sure you are starting from the current master branch
git checkout master
git pull

# Create a new branch (called <branch-name> in this case)
git checkout -b <branch-name>
```

Once you have created commits addressing the issue, you can push them to the remote branch. On the first push, you will be prompted to create a new merge request (MR). If the CI doesn't pass yet and you're still working on it, you can set the MR in **Draft** mode. Once it's ready, you can disable that mode and ask for a review from a **Maintainer**.

## Linter

Code syntax is analyzed before submitting the code.

To run the linter tools suite you may use [pre-commit](https://pre-commit.com).

```shell
pre-commit run -a
```

This checks for common coding issues and regressions. This will also be run on CI and the code **won't be merged** if this check doesn't pass.

## Tests

Tests are executed with [tox](https://tox.wiki) using [pytest](https://pytest.org).

```shell
tox
```

To recreate tox virtual environment (e.g. a dependencies update), you may run `tox -r`.

This checks for regressions on the code and validates the behavior of new features. This will also be run on CI and the code **won't be merged** if this check doesn't pass.

## Documentation

This documentation uses [Sphinx](http://www.sphinx-doc.org/) and was generated using [MkDocs](https://mkdocs.org/) and [mkdocstrings](https://mkdocstrings.github.io/).

### Setup

Add the `docs` extra when installing `bio-parser`:

```shell
# In a clone of the Git repository
pip install .[docs]
```

Build the documentation using `mkdocs serve -v`. You can then write in [Markdown](https://www.markdownguide.org/) in the relevant `docs/*.md` files, and see live output on <http://localhost:8000>.
