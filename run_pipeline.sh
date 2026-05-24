#!/bin/bash
# End-to-end Nested ETER pipeline.
#
# Given:
#   ./hypotheses/   word-level .bio hypothesis files
#   ./labels/       word-level .bio reference files
#
# this script will:
#   1. Synchronise filenames across hypotheses/ and labels/ (creates
#      dummy .bio files where needed).
#   2. Generate char-level .bio files into char_hypotheses/ and
#      char_labels/.
#   3. Run `bio-parser validate --allow-nested` over every .bio file
#      in each of the four folders, producing sibling .json files.
#   4. Convert every .json file in each of the four folders into a
#      sibling .pkl file with `json_to_pkl.py`.
#   5. Run the full ETER evaluation suite via
#      `time_measurement_evaluation.sh`.
#
# Each tool only touches files matching its expected extension, so the
# folders may safely contain the .bio / .json / .pkl artefacts
# side-by-side after the run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

HYP_DIR="${HYP_DIR:-hypotheses}"
LABELS_DIR="${LABELS_DIR:-labels}"
CHAR_HYP_DIR="${CHAR_HYP_DIR:-char_hypotheses}"
CHAR_LABELS_DIR="${CHAR_LABELS_DIR:-char_labels}"

VENV_DIR="${VENV_DIR:-.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SKIP_VENV="${SKIP_VENV:-0}"

log() {
    printf '\n\033[1;34m==> %s\033[0m\n' "$*"
}

# Bootstrap a local virtualenv at ${VENV_DIR} on first run and activate
# it for the rest of the script. Set SKIP_VENV=1 to use whatever
# interpreter and CLIs are already on PATH (useful inside Docker or
# when the user manages their own environment).
bootstrap_venv() {
    if [[ "${SKIP_VENV}" == "1" ]]; then
        log "SKIP_VENV=1 set -- using ambient Python environment"
        return
    fi

    if [[ ! -d "${VENV_DIR}" ]]; then
        log "Creating Python virtual environment at ${VENV_DIR}"
        if ! "${PYTHON_BIN}" -m venv "${VENV_DIR}"; then
            echo "ERROR: failed to create virtualenv. On Debian/Ubuntu install" >&2
            echo "       'python3-venv' (e.g. 'sudo apt install python3-venv')." >&2
            exit 1
        fi

        # shellcheck disable=SC1091
        source "${VENV_DIR}/bin/activate"

        log "Installing dependencies into ${VENV_DIR} (one-time)"
        pip install --upgrade pip >/dev/null
        pip install -r "${SCRIPT_DIR}/requirements.txt"
    else
        # shellcheck disable=SC1091
        source "${VENV_DIR}/bin/activate"
    fi

    PYTHON_BIN="$(command -v python)"
}

require_dir() {
    local dir="$1"
    if [[ ! -d "${dir}" ]]; then
        echo "ERROR: required input directory '${dir}' does not exist." >&2
        exit 1
    fi
}

require_cmd() {
    local cmd="$1"
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        echo "ERROR: command '${cmd}' not found in PATH." >&2
        echo "Did you run 'pip install -r requirements.txt'?" >&2
        exit 1
    fi
}

# Run bio-parser on every .bio file in the given directory.
# Skips silently if there are no .bio files.
parse_bio_folder() {
    local dir="$1"
    log "Running bio-parser on ${dir}/*.bio"

    # Build the list of .bio files explicitly so we never accidentally
    # pass .json / .pkl artefacts to the parser.
    local files=()
    while IFS= read -r -d '' f; do
        files+=("${f}")
    done < <(find "${dir}" -maxdepth 1 -type f -name '*.bio' -print0)

    if [[ "${#files[@]}" -eq 0 ]]; then
        echo "No .bio files found in ${dir}, skipping."
        return
    fi

    bio-parser validate --allow-nested "${files[@]}"
}

# Convert .json -> .pkl in the given directory.
convert_json_folder() {
    local dir="$1"
    log "Converting JSON to PKL in ${dir}"
    "${PYTHON_BIN}" "${SCRIPT_DIR}/json_to_pkl.py" "${dir}"
}

bootstrap_venv

log "Checking prerequisites"
require_dir "${HYP_DIR}"
require_dir "${LABELS_DIR}"
require_cmd bio-parser
require_cmd compute-eter

mkdir -p "${CHAR_HYP_DIR}" "${CHAR_LABELS_DIR}"

log "Step 1/5 -- Synchronising .bio filenames across ${HYP_DIR} and ${LABELS_DIR}"
"${PYTHON_BIN}" "${SCRIPT_DIR}/fix_bio_folders.py" \
    --hypotheses-dir "${HYP_DIR}" \
    --labels-dir     "${LABELS_DIR}"

log "Step 2/5 -- Generating char-level .bio files"
"${PYTHON_BIN}" "${SCRIPT_DIR}/word_to_char_bio.py" "${HYP_DIR}"    "${CHAR_HYP_DIR}"
"${PYTHON_BIN}" "${SCRIPT_DIR}/word_to_char_bio.py" "${LABELS_DIR}" "${CHAR_LABELS_DIR}"

log "Step 3/5 -- Parsing .bio files into .json with bio-parser"
parse_bio_folder "${HYP_DIR}"
parse_bio_folder "${LABELS_DIR}"
parse_bio_folder "${CHAR_HYP_DIR}"
parse_bio_folder "${CHAR_LABELS_DIR}"

log "Step 4/5 -- Converting .json files into .pkl"
convert_json_folder "${HYP_DIR}"
convert_json_folder "${LABELS_DIR}"
convert_json_folder "${CHAR_HYP_DIR}"
convert_json_folder "${CHAR_LABELS_DIR}"

log "Step 5/5 -- Running ETER evaluation"
LABELS_DIR="${LABELS_DIR}/" \
HYP_DIR="${HYP_DIR}/" \
CHAR_LABELS_DIR="${CHAR_LABELS_DIR}/" \
CHAR_HYP_DIR="${CHAR_HYP_DIR}/" \
    bash "${SCRIPT_DIR}/time_measurement_evaluation.sh"

log "Pipeline complete. See evaluation_report.txt for the metrics."
