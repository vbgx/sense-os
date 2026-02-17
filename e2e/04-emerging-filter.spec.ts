import { test, expect } from '@playwright/test';
import { DEFAULT_VERTICAL_ID } from "./utils/env";

test('Emerging only filter works', async ({ page }) => {
  await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}&emerging_only=true`);

  await page.waitForSelector('[data-testid="opportunity-row"]');

  const statuses = await page.locator('[data-testid="timing-status"]').allTextContents();

  for (const status of statuses) {
    expect(status).toBe('EARLY');
  }
});
