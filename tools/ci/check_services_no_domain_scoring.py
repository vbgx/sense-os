from __future__ import annotations

import sys
from pathlib import Path


FORBIDDEN = [
    "/scoring/",
    "/metrics/",
]

ALLOWLIST_FILES = {
    # ok: thin forwarders to domain only (single import line)
    "services/processing_worker/src/processing_worker/features/language.py",
    "services/processing_worker/src/processing_worker/features/spam.py",
    "services/processing_worker/src/processing_worker/features/signal_quality.py",
    "services/processing_worker/src/processing_worker/features/pain_score.py",
    "services/processing_worker/src/processing_worker/features/vertical_auto.py",
    "services/clustering_worker/src/clustering_worker/storage/severity.py",
    "services/clustering_worker/src/clustering_worker/storage/recurrence.py",
    "services/clustering_worker/src/clustering_worker/storage/monetizability.py",
    "services/clustering_worker/src/clustering_worker/storage/contradiction.py",
    "services/clustering_worker/src/clustering_worker/storage/competitive_heat.py",
    "services/clustering_worker/src/clustering_worker/storage/persona.py",
}


def main() -> int:
    root = Path(".")
    offenders: list[str] = []

    for p in root.glob("services/**/src/**/*.py"):
        rel = str(p.as_posix())
        if rel in ALLOWLIST_FILES:
            continue

        if any(seg in rel for seg in FORBIDDEN):
            offenders.append(rel)

    if offenders:
        print("services contain forbidden business-logic modules (must live in packages/domain):")
        for o in sorted(offenders):
            print(f" - {o}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
