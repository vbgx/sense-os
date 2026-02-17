from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = ROOT / "src" / "domain"

FORBIDDEN_PREFIXES = ("pydantic", "sqlalchemy", "fastapi", "redis")


def _check_file(path: Path) -> list[str]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith(FORBIDDEN_PREFIXES):
                    violations.append(f"{path}:{node.lineno}: import {name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith(FORBIDDEN_PREFIXES):
                violations.append(f"{path}:{node.lineno}: from {module} import ...")

    return violations


def test_domain_has_no_infra_deps() -> None:
    assert DOMAIN_ROOT.exists(), f"domain root not found: {DOMAIN_ROOT}"

    violations: list[str] = []
    for path in DOMAIN_ROOT.rglob("*.py"):
        violations.extend(_check_file(path))

    assert not violations, "\n".join(["Forbidden infra deps in domain:", *sorted(violations)])
