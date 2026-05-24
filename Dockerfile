# Nested ETER end-to-end pipeline image.
#
# Build:
#   docker build -t nested-eter .
#
# Run (mount the four data folders into /data and let the pipeline
# operate on them):
#   docker run --rm \
#       -v "$PWD/hypotheses:/data/hypotheses" \
#       -v "$PWD/labels:/data/labels" \
#       -v "$PWD/char_hypotheses:/data/char_hypotheses" \
#       -v "$PWD/char_labels:/data/char_labels" \
#       -v "$PWD:/data/report" \
#       nested-eter
#
# The container writes evaluation_report.txt into /data/report (i.e. the
# host's working directory). See docker_run.sh for a convenience
# wrapper that handles all of this automatically.

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SKIP_VENV=1 \
    HYP_DIR=/data/hypotheses \
    LABELS_DIR=/data/labels \
    CHAR_HYP_DIR=/data/char_hypotheses \
    CHAR_LABELS_DIR=/data/char_labels

WORKDIR /app

# Copy only the metadata first so Docker can cache the heavy
# `pip install` layer until requirements actually change.
COPY pyproject.toml README.md requirements.txt /app/
COPY nested_eter /app/nested_eter
COPY bio-parser-support-nested-entities /app/bio-parser-support-nested-entities

RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Application code (pipeline scripts and Python helpers).
COPY fix_bio_folders.py word_to_char_bio.py json_to_pkl.py \
     run_pipeline.sh time_measurement_evaluation.sh /app/

RUN chmod +x /app/run_pipeline.sh /app/time_measurement_evaluation.sh \
 && mkdir -p /data/hypotheses /data/labels \
             /data/char_hypotheses /data/char_labels /data/report

# All pipeline outputs (including evaluation_report.txt) end up in
# /data/report on the container side. Mount your host folder there.
WORKDIR /data/report

ENTRYPOINT ["/app/run_pipeline.sh"]
