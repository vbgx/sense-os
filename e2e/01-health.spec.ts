import { test, expect } from '@playwright/test';
import { API_BASE } from "./utils/env";

test('API health is OK', async ({ request }) => {
  const res = await request.get(`${API_BASE}/health`);
  expect(res.status()).toBe(200);
});
