import { test, expect } from "@playwright/test";
import { API_BASE, DEFAULT_VERTICAL_ID } from "./utils/env";

test.describe("API smoke (aligned with FastAPI routers)", () => {

  test("GET /health", async ({ request }) => {
    const r = await request.get(`${API_BASE}/health`);
    expect(r.status()).toBe(200);
    const json = await r.json();
    expect(json).toEqual({ status: "ok" });
  });

  test("GET /verticals/", async ({ request }) => {
    const r = await request.get(`${API_BASE}/verticals/`);
    expect([200].includes(r.status())).toBeTruthy();
    const data = await r.json();
    expect(Array.isArray(data)).toBe(true);
  });

  test("GET /clusters requires vertical_id", async ({ request }) => {
    const r = await request.get(`${API_BASE}/clusters`);
    expect(r.status()).toBe(422);
  });

  test("GET /clusters paginated", async ({ request }) => {
    const r = await request.get(
      `${API_BASE}/clusters?vertical_id=${DEFAULT_VERTICAL_ID}&limit=5&offset=0`
    );
    expect(r.status()).toBe(200);
    const data = await r.json();
    expect(data).toHaveProperty("total");
    expect(data).toHaveProperty("items");
    expect(data).toHaveProperty("limit", 5);
    expect(data).toHaveProperty("offset", 0);
  });

  test("GET /insights/top_pains", async ({ request }) => {
    const r = await request.get(`${API_BASE}/insights/top_pains?limit=5`);
    expect([200, 204].includes(r.status())).toBeTruthy();

    if (r.status() === 200) {
      const data = await r.json();
      expect(Array.isArray(data)).toBe(true);
      if (data.length >= 1) {
        expect(data[0]).toHaveProperty("exploitability_score");
        expect(data[0]).toHaveProperty("vertical_id");
        expect(data[0]).toHaveProperty("saturation_score");
      }
    }
  });

  test("GET /insights/emerging_opportunities", async ({ request }) => {
    const r = await request.get(`${API_BASE}/insights/emerging_opportunities?limit=10`);
    expect([200, 204].includes(r.status())).toBeTruthy();
  });

  test("GET /insights/declining_risks", async ({ request }) => {
    const r = await request.get(`${API_BASE}/insights/declining_risks?limit=10`);
    expect([200, 204].includes(r.status())).toBeTruthy();
  });

  test("GET /insights/{cluster_id}/export", async ({ request }) => {
    const r = await request.get(`${API_BASE}/insights/test-cluster-id/export`);
    expect([200, 404, 422].includes(r.status())).toBeTruthy();
  });

});
