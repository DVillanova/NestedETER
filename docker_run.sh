#!/bin/bash
# Convenience wrapper around the Nested ETER Docker image.
#
# - Builds the `nested-eter` image on first use (or when --rebuild is passed).
# - Mounts the four data folders from the current working directory into
#   the container and runs the full pipeline.
# - The container writes evaluation_report.txt (and any .json/.pkl
#   sibling files) back into the host folders.
#
# Usage:
#   ./docker_run.sh                # build if needed, then run
#   ./docker_run.sh --rebuild      # force-rebuild the image first
#   IMAGE_TAG=my-tag ./docker_run.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_TAG="${IMAGE_TAG:-nested-eter:latest}"

REBUILD=0
for arg in "$@"; do
    case "${arg}" in
        --rebuild) REBUILD=1 ;;
        -h|--help)
            sed -n '2,18p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown argument: ${arg}" >&2
            exit 2
            ;;
    esac
done

if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker is not installed or not on PATH." >&2
    exit 1
fi

if [[ "${REBUILD}" == "1" ]] || ! docker image inspect "${IMAGE_TAG}" >/dev/null 2>&1; then
    echo "==> Building Docker image ${IMAGE_TAG}"
    docker build -t "${IMAGE_TAG}" "${SCRIPT_DIR}"
fi

# Ensure the host folders exist so the bind-mounts don't create
# root-owned directories on the host.
mkdir -p hypotheses labels char_hypotheses char_labels

echo "==> Running pipeline in ${IMAGE_TAG}"
docker run --rm \
    -u "$(id -u):$(id -g)" \
    -v "$PWD/hypotheses:/data/hypotheses" \
    -v "$PWD/labels:/data/labels" \
    -v "$PWD/char_hypotheses:/data/char_hypotheses" \
    -v "$PWD/char_labels:/data/char_labels" \
    -v "$PWD:/data/report" \
    "${IMAGE_TAG}"
