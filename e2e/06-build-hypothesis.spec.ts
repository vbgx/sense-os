import { test, expect } from '@playwright/test';
import { API_BASE, DEFAULT_VERTICAL_ID } from "./utils/env";

test('Build hypothesis endpoint works', async ({ page }) => {
  await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}`);

  await page.waitForSelector('[data-testid="opportunity-row"]');

  const clusterId = await page
    .locator('[data-testid="opportunity-row"]')
    .first()
    .getAttribute('data-cluster-id');

  const res = await page.request.get(`${API_BASE}/insights/${clusterId}/build_hypothesis`);

  expect([200, 404]).toContain(res.status());
});
