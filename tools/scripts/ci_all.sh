#!/usr/bin/env bash
set -euo pipefail

make lint
make test
pytest -q tests/contract/inter_workers
make typecheck-web
