from __future__ import annotations

import glob
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "config" / "verticals"

def main() -> int:
    paths = sorted(DIR.glob("*.yml"))
    if not paths:
        print("No YAML found in config/verticals", file=sys.stderr)
        return 1

    ok = 0
    for p in paths:
        try:
            yaml.safe_load(p.read_text(encoding="utf-8"))
            ok += 1
        except Exception as e:
            print(f"[YAML ERROR] {p}: {e}", file=sys.stderr)
            return 2

    print(f"ok: loaded {ok} yaml files from {DIR}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
