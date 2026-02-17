// web/src/lib/api/client.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly url: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store", // important pour “live feel”
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`API request failed: ${res.status} ${text}`.trim(), res.status, url);
  }

  return (await res.json()) as T;
}
