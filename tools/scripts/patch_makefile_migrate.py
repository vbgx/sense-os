from __future__ import annotations

import re
from pathlib import Path

MAKEFILE = Path("Makefile")
s = MAKEFILE.read_text(encoding="utf-8")

replacement = (
    "migrate:\n"
    "\t@COMPOSE_FILE=$(COMPOSE_FILE) ./tools/scripts/migrate.sh\n"
)

m = re.search(r"(?m)^[A-Za-z0-9_.-]+:\s*$", s)
# Replace only the migrate target block
pattern = re.compile(
    r"(?ms)^migrate:\s*\n(?:\t.*\n)*"
)

if not pattern.search(s):
    raise SystemExit("migrate target not found in Makefile")

s2 = pattern.sub(replacement, s, count=1)
MAKEFILE.write_text(s2, encoding="utf-8")
print("OK: Makefile migrate target updated")
