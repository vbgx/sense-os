from __future__ import annotations

import ast
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
API_ROOT = ROOT / "apps" / "api_gateway" / "src" / "api_gateway"

ALLOWED_PREFIXES = ("db.adapters",)


def is_violation(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        for alias in node.names:
            name = alias.name
            if name == "db" or name.startswith("db."):
                if not name.startswith(ALLOWED_PREFIXES):
                    return True
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        if module == "db" or module.startswith("db."):
            if module.startswith(ALLOWED_PREFIXES):
                return False
            if module == "db":
                for alias in node.names:
                    if alias.name == "adapters":
                        return False
            return True
    return False


def main() -> int:
    if not API_ROOT.exists():
        print(f"API root not found: {API_ROOT}", file=sys.stderr)
        return 1

    violations: list[str] = []
    for path in API_ROOT.rglob("*.py"):
        src = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(src, filename=str(path))
        except SyntaxError as exc:
            violations.append(f"{path}:{exc.lineno}:{exc.offset}: syntax error: {exc}")
            continue

        for node in ast.walk(tree):
            if is_violation(node):
                lineno = getattr(node, "lineno", "?")
                violations.append(f"{path}:{lineno}: disallowed db import")

    if violations:
        print("Disallowed db imports found in api_gateway:")
        for v in sorted(set(violations)):
            print(f"- {v}")
        return 1

    print("OK: no disallowed db imports in api_gateway")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
