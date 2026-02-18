#!/usr/bin/env bash
set -euo pipefail

python tools/ci/check_services_no_domain_scoring.py
pytest -q tests/test_domain_has_no_infra_imports_strict.py
