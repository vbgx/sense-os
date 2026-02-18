import { test, expect } from "@playwright/test";

test("overview loads and shows Market Pulse + Breakouts", async ({ page }) => {
  await page.goto("/overview");

  // Header / updated badge (selon ton composant)
  await expect(page.getByText(/Overview/i)).toBeVisible();

  // KPI labels (contrat UX)
  await expect(page.getByText("Active Verticals")).toBeVisible();
  await expect(page.getByText("Emerging (7d)")).toBeVisible();
  await expect(page.getByText("Declining")).toBeVisible();

  // Breakouts table should exist
  // (adapte le selector si tu as une table shadcn)
  await expect(page.getByText(/Top Breakouts/i)).toBeVisible();
});
