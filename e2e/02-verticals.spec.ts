import { test, expect } from '@playwright/test';

test('Verticals list loads', async ({ page }) => {
  await page.goto('/verticals');

  await page.waitForSelector('[data-testid="vertical-row"]');

  const options = await page.locator('[data-testid="vertical-row"]').count();
  expect(options).toBeGreaterThan(0);
});
