import { test, expect } from '@playwright/test';
import { DEFAULT_VERTICAL_ID } from "./utils/env";

test('Cluster detail loads and shows timeline', async ({ page }) => {
  await page.goto(`/opportunities?vertical_id=${DEFAULT_VERTICAL_ID}`);

  await page.waitForSelector('[data-testid="opportunity-row"]');

  const clusterId = await page
    .locator('[data-testid="opportunity-row"]')
    .first()
    .getAttribute('data-cluster-id');

  await page.goto(`/clusters/${clusterId}`);

  await page.waitForSelector('[data-testid="cluster-title"]');
  await page.waitForSelector('[data-testid="timeline-chart"]');
});
