import { API_BASE } from "./env";

export async function healthCheck(request) {
  const res = await request.get(`${API_BASE}/health`);
  return res.status();
}
