import { API_BASE_URL } from "@/lib/api/meta";

export type ApiErrorShape = {
  status: number;
  message: string;
  details?: unknown;
};

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor({ status, message, details }: ApiErrorShape) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

type FetchJsonOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
};

function hasMessageField(x: unknown): x is { message: string } {
  if (typeof x !== "object" || x === null) return false;
  if (!("message" in x)) return false;
  return typeof (x as { message?: unknown }).message === "string";
}

async function readErrorDetails(res: Response): Promise<unknown> {
  const contentType = res.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    try {
      return await res.json();
    } catch {
      return undefined;
    }
  }

  try {
    return await res.text();
  } catch {
    return undefined;
  }
}

export async function fetchJson<T>(
  path: string,
  opts: FetchJsonOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;

  const res = await fetch(url, {
    method: opts.method ?? "GET",
    headers: {
      "content-type": "application/json",
      ...(opts.headers ?? {}),
    },
    body: opts.body === undefined ? undefined : JSON.stringify(opts.body),
    signal: opts.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const details = await readErrorDetails(res);

    const message = hasMessageField(details)
      ? details.message
      : `API request failed: ${res.status} ${res.statusText}`;

    throw new ApiError({ status: res.status, message, details });
  }

  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    throw new ApiError({
      status: res.status,
      message: "API returned non-JSON response",
      details: { contentType },
    });
  }

  return (await res.json()) as T;
}
