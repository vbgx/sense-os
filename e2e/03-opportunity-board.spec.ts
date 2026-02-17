import { test, expect } from '@playwright/test';
import { DEFAULT_VERTICAL_ID } from "./utils/env";

test('Top pains list renders', async ({ page }) => {
  await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}`);

  await page.waitForSelector('[data-testid="opportunity-row"]');

  const rows = await page.locator('[data-testid="opportunity-row"]').count();
  expect(rows).toBeGreaterThan(0);
});

test('Sorting by exploitability works', async ({ page }) => {
  await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}`);

  await page.waitForSelector('[data-testid="opportunity-row"]');

  const first = await page.locator('[data-testid="pain-score"]').first().innerText();
  const second = await page.locator('[data-testid="pain-score"]').nth(1).innerText();

  expect(parseInt(first)).toBeGreaterThanOrEqual(parseInt(second));
});
