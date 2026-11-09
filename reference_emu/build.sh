#!/bin/sh
# Build the web emulator: firmware sources -> wasm32 (system clang+lld),
# then copy the web shell into dist/. Builds both firmwares:
#   sloop.wasm    from $SLOOP   (isod89/sloop-fm1)
#   felucca.wasm  from $FELUCCA (hugelton/Felucca), if present
set -e
cd "$(dirname "$0")"
SLOOP=${SLOOP:-$(cd "$(dirname "$0")/.." && pwd)}
FELUCCA=${FELUCCA:-$HOME/Projects/Felucca}

CFLAGS="--target=wasm32 -O2 -fno-builtin -ffreestanding -nostdlib \
    -Wall -Wno-unused-function -Wno-unused-variable"
LDFLAGS="-Wl,--no-entry -Wl,--export-memory \
    -Wl,-z,stack-size=1048576 -Wl,--global-base=1048576"

test -f "$SLOOP/build/gen/felucca_tables.h" || {
    echo "SLOOP generated headers missing; run the gen_*.py tools in $SLOOP first" >&2
    exit 1
}

mkdir -p dist
clang $CFLAGS -I "$SLOOP/build/gen" -I "$SLOOP/firmware/src" -I "$SLOOP/firmware/hal" \
    $LDFLAGS -o dist/sloop.wasm sloop_wasm.c

if [ -f "$FELUCCA/build/gen/felucca_tables.h" ] && [ -f "felucca_wasm.c" ]; then
    clang $CFLAGS -I "$FELUCCA/build/gen" -I "$FELUCCA/firmware/src" \
        $LDFLAGS -o dist/felucca.wasm felucca_wasm.c
else
    echo "note: Felucca generated headers or source missing; skipping felucca.wasm" >&2
fi

cp index.html emu.js worklet.js manifest.webmanifest dist/
# Keep the GitHub Pages bundle in sync with the freshly compiled firmware.
if [ -d "$SLOOP/docs/dub" ]; then
    cp dist/sloop.wasm "$SLOOP/docs/dub/sloop.wasm"
    cp index.html emu.js worklet.js manifest.webmanifest "$SLOOP/docs/dub/"
fi
ls -la dist/
