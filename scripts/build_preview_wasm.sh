#!/bin/sh
# Build docs/webapp/editor/sloop-preview.wasm with zig cc (no system clang in the sandbox).
# Same recipe as tools/build_preview.py's clang path: freestanding wasm32 + tools/wasm_shim.
set -e
cd "$(dirname "$0")/.."
mkdir -p build/preview
python3 -m ziglang cc --target=wasm32-freestanding -O2 -fno-builtin -ffreestanding \
    -c tools/wasm_shim/mem.c -o build/preview/mem.o
EXPORTS=""
for n in init buffer frames rate track param global select step locks \
         fm6 sample kit hit note play position panic render \
         dub_enable dub_siren dub_band; do
    EXPORTS="$EXPORTS -Wl,--export=preview_$n"
done
python3 -m ziglang cc --target=wasm32-freestanding -O2 -fwrapv -fno-strict-aliasing \
    -ffreestanding -nostdlib -w \
    -Itools/wasm_shim -Ibuild/gen -Ifirmware/src \
    firmware/host/preview.c build/preview/mem.o \
    -Wl,--no-entry -Wl,--export-memory -Wl,--initial-memory=16777216 -Wl,-z,stack-size=131072 \
    $EXPORTS \
    -o build/preview/sloop-preview.wasm
cp build/preview/sloop-preview.wasm docs/webapp/editor/sloop-preview.wasm
ls -l docs/webapp/editor/sloop-preview.wasm
