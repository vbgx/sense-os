const fs = require('fs');
const path = require('path');
const { defineConfig } = require('@playwright/test');

const root = __dirname;
const apiHost = process.env.E2E_API_HOST || '127.0.0.1';
const apiPort = process.env.E2E_API_PORT || '8000';
const uiPort = process.env.E2E_UI_PORT || '3000';

const apiBase = process.env.API_BASE_URL || `http://${apiHost}:${apiPort}`;
const uiBase = process.env.PLAYWRIGHT_BASE_URL || `http://localhost:${uiPort}`;

process.env.API_BASE_URL = apiBase;
process.env.PLAYWRIGHT_BASE_URL = uiBase;

const pythonPath = [
  path.join(root, 'apps/api_gateway/src'),
  path.join(root, 'packages/application/src'),
  path.join(root, 'packages/db/src'),
  path.join(root, 'packages/domain/src'),
  path.join(root, 'packages/queue/src'),
  path.join(root, 'services/scheduler/src'),
].join(path.delimiter);

const venvPython = path.join(root, '.venv', 'bin', 'python');
const pythonCmd =
  process.env.E2E_PYTHON ||
  process.env.PYTHON ||
  (fs.existsSync(venvPython) ? venvPython : 'python3');

module.exports = defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: uiBase,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: [
    {
      command: `${pythonCmd} tools/scripts/run_e2e_api.py`,
      url: `${apiBase}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        PYTHONPATH: pythonPath,
        E2E_DB_PATH: path.join(root, '.tmp', 'sense_os_e2e.db'),
        E2E_API_HOST: apiHost,
        E2E_API_PORT: String(apiPort),
        E2E_API_LOG_LEVEL: process.env.E2E_API_LOG_LEVEL || 'info',
      },
    },
    {
      command: 'node tools/scripts/ensure_ui_node_modules.js && cd apps/web && pnpm dev',
      url: uiBase,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        PORT: String(uiPort),
        NEXT_PUBLIC_API_BASE_URL: apiBase,
        NODE_PATH: path.join(root, 'apps/web/node_modules'),
      },
    },
  ],
});
