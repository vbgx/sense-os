import { test, expect } from "@playwright/test";
import { DEFAULT_VERTICAL_ID } from "./utils/env";

test.describe("UI — Cluster Deep Dive", () => {

  test("navigate board -> deep dive", async ({ page }) => {
    await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}`);

    const rows = page.locator('[data-testid="opportunity-row"]');
    if (await rows.count() === 0) {
      test.skip(true, "No data available");
    }

    await rows.first().click();
    await page.click('[data-testid="drawer-open-deep-dive"]');

    await expect(page).toHaveURL(/\/clusters\/\d+/);
    await expect(page.locator('[data-testid="cluster-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="timeline-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="score-breakdown"]')).toBeVisible();
  });

});
