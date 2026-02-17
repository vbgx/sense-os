import { test, expect } from "@playwright/test";
import { mockApi, assertPerfBudget } from "./_helpers";

test.describe("Sense Web UI – smoke", () => {
  test.beforeEach(async ({ page }) => {
    await mockApi(page);
  });

  test("Overview loads (no crash) + perf budget", async ({ page }) => {
    await page.goto("/overview");
    await expect(page.locator("h1")).toBeVisible();
    await assertPerfBudget(page, { domContentLoadedMs: 4000, loadMs: 7000 });
  });

  test("Opportunities board renders rows + perf budget", async ({ page }) => {
    await page.goto("/opportunities");
    await expect(page.locator("h1")).toContainText("Opportunities");
    await expect(page.locator("text=Summary")).toBeVisible();
    await expect(page.locator("text=SaaS spend")).toBeVisible();
    await assertPerfBudget(page, { domContentLoadedMs: 4000, loadMs: 7000 });
  });

  test("Inspect drawer opens from board and exposes deep dive link", async ({ page }) => {
    await page.goto("/opportunities");
    await expect(page.locator("text=SaaS spend")).toBeVisible();

    await page.locator("text=SaaS spend").click();

    const drawer = page.getByTestId("cluster-inspect-drawer");
    await expect(drawer).toBeVisible();
    await expect(drawer.locator("text=Inspect")).toBeVisible();
    await expect(drawer.locator("text=Open Deep Dive")).toBeVisible();
  });
});
