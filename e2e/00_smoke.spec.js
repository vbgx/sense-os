const { test, expect } = require('@playwright/test');

test('playwright runs', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/.*/);
});
