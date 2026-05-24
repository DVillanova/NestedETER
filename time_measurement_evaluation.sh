#!/bin/bash
# Run the full ETER evaluation suite (word- and char-level, both
# macro/micro and ordered/unordered variants) and time each call.
#
# The script assumes that:
#   - ./labels/             contains the word-level reference  .pkl files
#   - ./hypotheses/         contains the word-level hypothesis .pkl files
#   - ./char_labels/        contains the char-level reference  .pkl files
#   - ./char_hypotheses/    contains the char-level hypothesis .pkl files
#
# Other files (.bio, .json, ...) in these folders are silently ignored by
# the `compute-eter` CLI.
set -euo pipefail

REPORT="evaluation_report.txt"

LABELS_DIR="${LABELS_DIR:-./labels/}"
HYP_DIR="${HYP_DIR:-./hypotheses/}"
CHAR_LABELS_DIR="${CHAR_LABELS_DIR:-./char_labels/}"
CHAR_HYP_DIR="${CHAR_HYP_DIR:-./char_hypotheses/}"

run_eter() {
    local label="$1"
    local average="$2"
    local order="$3"
    local ref_dir="$4"
    local hyp_dir="$5"

    {
        echo "--- ${label} ---"
        local ts tt
        ts=$(date +%s%N)
        compute-eter "${average}" "${order}" "${ref_dir}" "${hyp_dir}"
        tt=$((($(date +%s%N) - ts) / 1000000))
        echo "Time taken: ${tt} ms"
        echo
    } >>"${REPORT}"
}

{
    echo "=================="
    echo "WORD LEVEL METRICS"
    echo "=================="
} >"${REPORT}"

run_eter "MACRO ORDERED"   macro ordered   "${LABELS_DIR}" "${HYP_DIR}"
run_eter "MICRO ORDERED"   micro ordered   "${LABELS_DIR}" "${HYP_DIR}"
run_eter "MACRO UNORDERED" macro unordered "${LABELS_DIR}" "${HYP_DIR}"
run_eter "MICRO UNORDERED" micro unordered "${LABELS_DIR}" "${HYP_DIR}"

{
    echo "=================="
    echo "CHAR LEVEL METRICS"
    echo "=================="
} >>"${REPORT}"

run_eter "MACRO ORDERED"   macro ordered   "${CHAR_LABELS_DIR}" "${CHAR_HYP_DIR}"
run_eter "MICRO ORDERED"   micro ordered   "${CHAR_LABELS_DIR}" "${CHAR_HYP_DIR}"
run_eter "MACRO UNORDERED" macro unordered "${CHAR_LABELS_DIR}" "${CHAR_HYP_DIR}"
run_eter "MICRO UNORDERED" micro unordered "${CHAR_LABELS_DIR}" "${CHAR_HYP_DIR}"

echo "Evaluation report written to ${REPORT}"
