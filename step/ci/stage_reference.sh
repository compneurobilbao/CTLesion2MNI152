#!/usr/bin/env bash
# Copy one fixture case (from fetch_pinned.sh output) to step/tests/reference/.
#   step/ci/stage_reference.sh FETCHED_DIR [case-01]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
src="${1:?}/fixtures/data/cases/${2:-case-01}"
dst="$here/../tests/reference"
mkdir -p "$dst"
cp "$src/ct.nii.gz" "$src/lesion_mask_native.nii.gz" "$src/lesion_mask_mni.nii.gz" "$dst/"
