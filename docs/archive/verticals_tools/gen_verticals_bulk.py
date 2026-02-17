from __future__ import annotations

import argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
VERT_DIR = ROOT / "config" / "verticals"
INDEX_PATH_JSON = VERT_DIR / "verticals.json"
INDEX_PATH = INDEX_PATH_JSONSEED_PATH = VERT_DIR / "_bulk_seed.tsv"

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

def dump_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

def parse_tsv(seed_path: Path) -> list[dict]:
    rows: list[dict] = []
    for raw in seed_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) < 6:
            raise SystemExit(f"Bad TSV line (need 6 columns): {raw}")

        vid, title, desc, tags_csv, queries_csv, sources_csv = parts[:6]
        tags = [t.strip() for t in tags_csv.split(",") if t.strip()]
        queries = [q.strip() for q in queries_csv.split("|") if q.strip()]
        sources = [s.strip() for s in sources_csv.split(",") if s.strip()]

        rows.append(
            {
                "id": vid,
                "title": title,
                "description": desc,
                "tags": tags,
                "default_queries": queries,
                "sources": sources,
            }
        )
    return rows

def next_priority(index: dict) -> int:
    items = index.get("verticals") or []
    if not items:
        return 10
    return max(int(v.get("priority", 0) or 0) for v in items) + 10

def ensure_index_entry(index: dict, vid: str, prio: int) -> bool:
    items = index.setdefault("verticals", [])
    if any(v.get("id") == vid for v in items):
        return False
    items.append({"id": vid, "file": f"{vid}.yml", "enabled": True, "priority": prio})
    return True

def ensure_vertical_file(row: dict, overwrite: bool) -> bool:
    path = VERT_DIR / f"{row['id']}.yml"
    if path.exists() and not overwrite:
        return False

    # ingestion block is optional; harmless if ignored
    ingestion_sources = []
    # basic mapping: each source gets a generic query from id/title
    # (still keep default_queries as the official compat contract)
    generic_q = row["id"].replace("_", " ")
    for s in row["sources"]:
        ingestion_sources.append({"name": s, "query": generic_q, "limit": 80})

    doc = {
        "id": row["id"],
        "name": row["id"],
        "title": row["title"],
        "description": row["description"],
        "version": 1,
        "enabled": True,
        "tags": row["tags"],
        "default_queries": row["default_queries"],
        "ingestion": {"sources": ingestion_sources} if ingestion_sources else None,
    }
    if doc.get("ingestion") is None:
        doc.pop("ingestion", None)

    dump_yaml(path, doc)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default=str(SEED_PATH), help="Path to _bulk_seed.tsv")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing per-vertical yml files")
    ap.add_argument("--limit", type=int, default=0, help="Only generate first N rows from seed (0=all)")
    args = ap.parse_args()

    seed_path = Path(args.seed)
    if not seed_path.exists():
        raise SystemExit(f"Seed file not found: {seed_path}")

    VERT_DIR.mkdir(parents=True, exist_ok=True)

    index = load_yaml(INDEX_PATH)
    if "verticals" not in index:
        index["verticals"] = []

    rows = parse_tsv(seed_path)
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    prio = next_priority(index)
    created_files = 0
    created_index = 0

    for row in rows:
        if ensure_vertical_file(row, overwrite=args.overwrite):
            created_files += 1
        if ensure_index_entry(index, row["id"], prio):
            created_index += 1
            prio += 10

    dump_yaml(INDEX_PATH, index)

    print("done")
    print("created/updated files:", created_files)
    print("new index entries:", created_index)
    print("index:", INDEX_PATH)

if __name__ == "__main__":
    main()
