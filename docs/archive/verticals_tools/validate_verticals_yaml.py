from __future__ import annotations

import glob
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "config" / "verticals"
ALLOWED_TIERS = {"core", "experimental", "long_tail"}
META_KEYS = {"audience", "function", "industry", "cluster", "member", "persona", "variant"}

def main() -> int:
    paths = sorted(DIR.glob("*.yml"))
    if not paths:
        print("No YAML found in config/verticals", file=sys.stderr)
        return 1

    ok = 0
    for p in paths:
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                print(f"[YAML ERROR] {p}: expected object", file=sys.stderr)
                return 2

            tier = data.get("tier")
            if tier is not None and str(tier) not in ALLOWED_TIERS:
                print(f"[YAML ERROR] {p}: invalid tier {tier!r}", file=sys.stderr)
                return 2

            meta = data.get("meta")
            if meta is not None:
                if not isinstance(meta, dict):
                    print(f"[YAML ERROR] {p}: meta must be an object", file=sys.stderr)
                    return 2
                extra = sorted(set(meta.keys()) - META_KEYS)
                if extra:
                    print(f"[YAML ERROR] {p}: meta has unexpected keys {extra!r}", file=sys.stderr)
                    return 2
                for k, v in meta.items():
                    if v is not None and not isinstance(v, str):
                        print(f"[YAML ERROR] {p}: meta.{k} must be string or null", file=sys.stderr)
                        return 2
            ok += 1
        except Exception as e:
            print(f"[YAML ERROR] {p}: {e}", file=sys.stderr)
            return 2

    print(f"ok: loaded {ok} yaml files from {DIR}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
