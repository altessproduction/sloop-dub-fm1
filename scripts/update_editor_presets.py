#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Syncs docs/webapp/editor/sloop-editor.html with the firmware's factory preset tables:
the web editor holds a JS mirror (P(name, e[8], env, mono, pat) per engine, FACTORY_PK for FM6).
  python3 scripts/update_editor_presets.py
Parses the C tables (eng_*.c, the generated SMP_PRESET_TABLE, FM6_PRESETS), regenerates
FACTORY_PK with tools/gen_fm6_patches.py --js, and rewrites the HTML blocks in place.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "docs/webapp/editor/sloop-editor.html"

# engine display name in the HTML -> (c file, table name); None = the generated SMP table
ENGINES = {
    "ANALOG": ("eng_analog.c", "ANALOG_PRESETS"),
    "DIGITAL": ("eng_digital.c", "DIGITAL_PRESETS"),
    "PHASE": ("eng_phase.c", "PHASE_PRESETS"),
    "LOFI": ("eng_lofi.c", "LOFI_PRESETS"),
    "SAMPLE": None,
    "VOICE": ("eng_formant.c", "FORMANT_PRESETS"),
    "TRIO": ("eng_trio.c", "TRIO_PRESETS"),
    "WHEEL": ("eng_drawbar.c", "DRAWBAR_PRESETS"),
    "GRAIN": ("eng_grain.c", "GRAIN_PRESETS"),
    "FM6": ("eng_fm6.c", "FM6_PRESETS"),
    "PHYS": ("eng_phys.c", "PHYS_PRESETS"),
    "NOISE": ("eng_noise.c", "NOISE_PRESETS"),
}

# the C identifiers that appear inside preset tables, as their values
ID_MAP = {
    "PM_MODAL": 0, "PM_STRING": 1, "PM_MEMB": 2, "PM_SYMP": 3,
    "NZ_ANLG": 0, "NZ_DUST": 1, "NZ_LFSR": 2, "NZ_META": 3,
    "SLC_DIV_AUTO": 4,
}


def _int(x):
    x = x.strip()
    return ID_MAP[x] if x in ID_MAP else int(x)


def read_table(text, name):
    """the entries of a C preset table as (name, e[8] list, env[4] list, mono, pat)"""
    i = text.find(f"{name}[] = {{")
    if i < 0:
        raise SystemExit(f"table {name} not found")
    j = text.find("\n};", i)                           # the table's closing brace (at line start)
    block = text[i:j]
    cut = block.find("#define")                        # a generated table: stop before the next macro
    if cut > 0:
        block = block[:cut]
    out = []
    k = 0
    while True:
        k = block.find('{"', k)
        if k < 0:
            break
        # the entry ends at the '}' that closes it: walk from k, depth over {} only
        p, depth = k, 0
        while p < len(block):
            c = block[p]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            p += 1
        entry = block[k:p]
        m = re.match(r'\{"([^"]+)",\s*\{([^{}]*)\},\s*\{([^{}]*)\},\s*(-?\d+),\s*(\d+)', entry)
        if m:
            pname = m.group(1)
            e = [_int(x) for x in m.group(2).split(",") if x.strip()]
            env = [_int(x) for x in m.group(3).split(",") if x.strip()]
            mono = int(m.group(5))
            mp = re.search(r"PAT\((\d+)\)", entry)
            pat = int(mp.group(1)) if mp else 0
            out.append((pname, e, env, mono, pat))
        k = p + 1
    return out


def js_list(entries):
    rows = []
    for pname, e, env, mono, pat in entries:
        pat_s = f", {pat}" if pat else ""
        rows.append(f'P("{pname}", [{", ".join(map(str, e))}], [{", ".join(map(str, env))}], {mono}{pat_s})')
    lines, cur = [], "       "
    for r in rows:
        piece = r + ", "
        if len(cur) + len(piece) > 150:
            lines.append(cur.rstrip())
            cur = "        "
        cur += piece
    lines.append(cur.rstrip().rstrip(","))
    return "\n".join(lines)


def replace_presets(html, engine, new_body):
    """rewrite the presets: [ ... ] of the engine's object in the ENG array"""
    i = html.find(f'name: "{engine}",')
    if i < 0:
        raise SystemExit(f'no engine {engine} in html')
    j = html.find("presets: [", i)
    if j < 0:
        raise SystemExit(f'no presets in {engine}')
    k = j + len("presets: ")
    if html[k] != "[":
        raise SystemExit("bad block shape")
    depth, k = 0, k
    while k < len(html):
        c = html[k]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return html[:j] + "presets: [\n" + new_body + "\n     " + html[k:]
        k += 1
    raise SystemExit("unbalanced presets block")


def main():
    html = HTML.read_text()
    gen = ROOT / "build/gen/felucca_samples.h"
    src_m = (ROOT / "tools/gen_samples.py").stat().st_mtime
    if not gen.exists() or gen.stat().st_mtime < src_m:
        subprocess.run([sys.executable, str(ROOT / "tools/gen_samples.py"), str(gen)], cwd=ROOT, check=True)
    sample_table = read_table(gen.read_text(), "SMP_PRESET_TABLE")

    for name, src in ENGINES.items():
        if name == "SAMPLE":
            entries = sample_table
        else:
            entries = read_table((ROOT / "firmware/src" / src[0]).read_text(), src[1])
        html = replace_presets(html, name, js_list(entries))
        print(f"{name}: {len(entries)} presets")

    # FACTORY_PK: the packed FM6 voices, as gen_fm6_patches.py --js prints them
    js = subprocess.run([sys.executable, str(ROOT / "tools/gen_fm6_patches.py"), "--js"], cwd=ROOT,
                        capture_output=True, text=True, check=True).stdout
    rows = [ln.strip() for ln in js.splitlines() if ln.strip().startswith("[")]
    body = "\n".join("    " + ln for ln in rows)
    i = html.find("const FACTORY_PK = [")
    j = html.find("];", i)
    if i < 0 or j < 0:
        raise SystemExit("no FACTORY_PK block")
    html = html[:i] + "const FACTORY_PK = [\n" + body + "\n" + html[j:]
    print("FACTORY_PK regenerated")
    HTML.write_text(html)
    print(f"-> {HTML}")


if __name__ == "__main__":
    main()
