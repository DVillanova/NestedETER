FROM python:3.10-slim

# Install package
WORKDIR /src
COPY requirements.txt doc-requirements.txt LICENSE setup.py pyproject.toml MANIFEST.in README.md /src/
COPY bio_parser /src/bio_parser

RUN pip install . --no-cache-dir
