#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-only
# The riddim bank's proof: the generator rewrites the compressed bank and the
# raw golden grids from the same run, then tests/riddim_check.c loads every
# riddim through dub.c's own loader and compares the four 64-step tracks, notes
# and velocities, against the grids -- the round trip is the proof. Run from the
# repo root (or anywhere: it cds to its own root):
#   sh tools/verify_riddims.sh
set -e
cd "$(dirname "$0")/.."
CC="${CC:-cc}"
mkdir -p build
python3 tools/gen_riddims_web.py --golden build/riddim_golden.h | tail -1
"$CC" -std=c99 -Wall -Wextra -I firmware/src -I build -o build/riddim_check \
    tests/riddim_check.c
./build/riddim_check
