import { expect, type Page } from "@playwright/test";
import topPains from "./fixtures/top_pains.json";
import verticals from "./fixtures/verticals.json";

export async function mockApi(page: Page) {
  // Match your API client: NEXT_PUBLIC_API_BASE_URL defaults to http://localhost:8000
  // We mock any host, only by path.
  await page.route("**/insights/top_pains**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(topPains),
    });
  });

  await page.route("**/verticals/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(verticals),
    });
  });

  // Optional: avoid noisy failing calls in other views
  await page.route("**/meta/status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        last_run_at: null,
        scoring_version: "heuristics_v1",
        total_signals_7d: 1234,
        total_clusters: 42,
      }),
    });
  });
}

export async function assertPerfBudget(page: Page, budget: { domContentLoadedMs: number; loadMs: number }) {
  const nav = await page.evaluate(() => {
    const e = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
    if (!e) return null;
    return {
      domContentLoaded: e.domContentLoadedEventEnd,
      load: e.loadEventEnd,
    };
  });

  // If navigation timing isn't available (rare), don't fail hard.
  if (!nav) return;

  expect(nav.domContentLoaded).toBeLessThan(budget.domContentLoadedMs);
  expect(nav.load).toBeLessThan(budget.loadMs);
}
