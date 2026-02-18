import ast
from pathlib import Path


FORBIDDEN_IMPORT_PREFIXES = (
    "sqlalchemy",
    "db",
    "redis",
    "httpx",
    "requests",
    "fastapi",
    "starlette",
    "psycopg",
    "psycopg2",
)


def test_domain_has_no_infra_imports_strict():
    root = Path("packages/domain/src/domain")
    py_files = list(root.rglob("*.py"))

    offenders = []

    for p in py_files:
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    if n.name.startswith(FORBIDDEN_IMPORT_PREFIXES):
                        offenders.append((str(p), n.name))
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    offenders.append((str(p), node.module))

    assert offenders == []
