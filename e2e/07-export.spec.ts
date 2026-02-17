import { test, expect } from '@playwright/test';
import { API_BASE, DEFAULT_VERTICAL_ID } from "./utils/env";

test('Export payload contract valid', async ({ page }) => {
  await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}`);

  await page.waitForSelector('[data-testid="opportunity-row"]');

  const clusterId = await page
    .locator('[data-testid="opportunity-row"]')
    .first()
    .getAttribute('data-cluster-id');

  const res = await page.request.get(`${API_BASE}/insights/${clusterId}/export`);

  if (res.status() === 200) {
    const data = await res.json();

    expect(data.export_version).toBe('ventureos_export_v1');
    expect(data.persona).toBeTruthy();
    expect(data.pain).toBeTruthy();
    expect(data.opportunity_score).toBeGreaterThanOrEqual(0);
  }
});
