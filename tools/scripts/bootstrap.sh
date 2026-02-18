#!/usr/bin/env bash
set -euo pipefail

uv sync
cd apps/web
pnpm install
