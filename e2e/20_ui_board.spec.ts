import { test, expect } from "@playwright/test";
import { DEFAULT_VERTICAL_ID } from "./utils/env";

test.describe("UI — Opportunity Board", () => {

  test("board renders", async ({ page }) => {
    await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}`);
    await expect(page.locator('[data-testid="opportunity-table"], [data-testid="empty-state"]')).toBeVisible();
  });

  test("row click opens inspect drawer", async ({ page }) => {
    await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}`);
    await page.waitForSelector('[data-testid="opportunity-row"]');
    await page.locator('[data-testid="opportunity-row"]').first().click();
    await expect(page).toHaveURL(/inspect=/);
    await expect(page.locator('[data-testid="cluster-inspect-drawer"]')).toBeVisible();
  });

});
