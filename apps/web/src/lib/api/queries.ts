"use client";

import { useQuery, type UseQueryOptions } from "@tanstack/react-query";

import {
  TopPainsSchema,
  ClusterDetailSchema,
  VerticalsResponseSchema,
  TrendListResponseSchema,
  OpsQueuesResponseSchema,
  OpsRunsResponseSchema,
} from "@/lib/api/schemas";

import type {
  TopPain,
  ClusterDetail,
  Vertical,
  TrendListResponse,
  OpsQueuesResponse,
  OpsRunsResponse,
} from "@/lib/api/schemas";

import {
  InsightsOverviewSchema,
  type InsightsOverview,
} from "@/lib/api/overview.schemas";

/* ──────────────────────────────────────────────────────────
 * API client (tiny, typed, no magic)
 * ────────────────────────────────────────────────────────── */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

type ApiGetOptions = {
  params?: Record<string, string | number | boolean | null | undefined>;
  signal?: AbortSignal;
};

function buildUrl(path: string, params?: ApiGetOptions["params"]) {
  const p = `${path.startsWith("/") ? "" : "/"}${path}`;
  const url = new URL(`${API_BASE_URL}${p}`);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v === null || v === undefined) continue;
      url.searchParams.set(k, String(v));
    }
  }
  return url.toString();
}

async function apiGetJson(path: string, opts: ApiGetOptions = {}) {
  const url = buildUrl(path, opts.params);

  const res = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal: opts.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status} ${res.statusText}${text ? ` — ${text}` : ""}`);
  }

  return (await res.json()) as unknown;
}

/* ──────────────────────────────────────────────────────────
 * Query keys (stable + centralized)
 * ────────────────────────────────────────────────────────── */

export const qk = {
  insights: {
    overview: (params: OverviewParams) => ["insights", "overview", params] as const,
    topPains: (params: TopPainsParams) => ["insights", "top_pains", params] as const,
    emerging: (params: ListParams) => ["insights", "emerging_opportunities", params] as const,
    declining: (params: ListParams) => ["insights", "declining_risks", params] as const,
    clusterDetail: (clusterId: string) => ["insights", "cluster_detail", clusterId] as const,
  },
  verticals: {
    list: () => ["verticals"] as const,
  },
  trends: {
    trending: (params: TrendingParams) => ["trending", params] as const,
  },
  ops: {
    queues: () => ["ops", "queues"] as const,
    runs: () => ["ops", "runs"] as const,
  },
};

/* ──────────────────────────────────────────────────────────
 * OVERVIEW
 * Endpoint: GET /insights/overview?window=7d&limit=10&offset=0
 * ────────────────────────────────────────────────────────── */

export type OverviewParams = {
  window?: string; // "7d" | "30d" | ...
  limit?: number;
  offset?: number;
  enabled?: boolean;
};

export function useInsightsOverview(
  params: OverviewParams = {},
  options?: UseQueryOptions<InsightsOverview>
) {
  return useQuery({
    queryKey: qk.insights.overview(params),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson("/insights/overview", {
        signal,
        params: {
          window: params.window ?? "7d",
          limit: params.limit ?? 10,
          offset: params.offset ?? 0,
        },
      });
      return InsightsOverviewSchema.parse(data);
    },
    staleTime: 30_000,
    enabled: params.enabled ?? true,
    ...options,
  });
}

/* ──────────────────────────────────────────────────────────
 * INSIGHTS — lists
 * ────────────────────────────────────────────────────────── */

export type ListParams = {
  vertical_id?: string | null;
  limit?: number;
  offset?: number;
};

export type TopPainsParams = ListParams & {
  tier?: string | null;
  emerging_only?: boolean;
};

export function useTopPains(params: TopPainsParams, options?: UseQueryOptions<TopPain[]>) {
  return useQuery({
    queryKey: qk.insights.topPains(params),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson("/insights/top_pains", {
        signal,
        params: {
          vertical_id: params.vertical_id ?? undefined,
          tier: params.tier ?? undefined,
          emerging_only: params.emerging_only ? true : undefined,
          limit: params.limit ?? 50,
          offset: params.offset ?? 0,
        },
      });
      return TopPainsSchema.parse(data);
    },
    staleTime: 30_000,
    ...options,
  });
}

export function useEmerging(params: ListParams, options?: UseQueryOptions<TopPain[]>) {
  return useQuery({
    queryKey: qk.insights.emerging(params),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson("/insights/emerging_opportunities", {
        signal,
        params: {
          vertical_id: params.vertical_id ?? undefined,
          limit: params.limit ?? 50,
          offset: params.offset ?? 0,
        },
      });
      return TopPainsSchema.parse(data);
    },
    staleTime: 30_000,
    ...options,
  });
}

export function useDeclining(params: ListParams, options?: UseQueryOptions<TopPain[]>) {
  return useQuery({
    queryKey: qk.insights.declining(params),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson("/insights/declining_risks", {
        signal,
        params: {
          vertical_id: params.vertical_id ?? undefined,
          limit: params.limit ?? 50,
          offset: params.offset ?? 0,
        },
      });
      return TopPainsSchema.parse(data);
    },
    staleTime: 30_000,
    ...options,
  });
}

export function useClusterDetail(
  cluster_id: string,
  enabled = true,
  options?: UseQueryOptions<ClusterDetail>
) {
  return useQuery({
    queryKey: qk.insights.clusterDetail(cluster_id),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson(`/insights/${encodeURIComponent(cluster_id)}`, { signal });
      return ClusterDetailSchema.parse(data);
    },
    enabled: Boolean(cluster_id) && enabled,
    staleTime: 30_000,
    ...options,
  });
}

/* ──────────────────────────────────────────────────────────
 * VERTICALS
 * ────────────────────────────────────────────────────────── */

export function useVerticals(options?: UseQueryOptions<Vertical[]>) {
  return useQuery({
    queryKey: qk.verticals.list(),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson("/verticals/", { signal });
      return VerticalsResponseSchema.parse(data).items;
    },
    staleTime: 60_000,
    ...options,
  });
}

/* ──────────────────────────────────────────────────────────
 * TRENDS
 * Endpoint: GET /trending?vertical_id=...
 * ────────────────────────────────────────────────────────── */

export type TrendingParams = {
  vertical_id: number;
  limit?: number;
  offset?: number;
  sparkline_days?: number;
  enabled?: boolean;
};

export function useTrending(params: TrendingParams, options?: UseQueryOptions<TrendListResponse>) {
  return useQuery({
    queryKey: qk.trends.trending(params),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson("/trending", {
        signal,
        params: {
          vertical_id: params.vertical_id,
          limit: params.limit ?? 20,
          offset: params.offset ?? 0,
          sparkline_days: params.sparkline_days ?? 30,
        },
      });
      return TrendListResponseSchema.parse(data);
    },
    enabled: params.enabled ?? true,
    staleTime: 30_000,
    ...options,
  });
}

/* ──────────────────────────────────────────────────────────
 * OPS (Transparency)
 * ────────────────────────────────────────────────────────── */

export function useOpsQueues(options?: UseQueryOptions<OpsQueuesResponse>) {
  return useQuery({
    queryKey: qk.ops.queues(),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson("/ops/queues", { signal });
      return OpsQueuesResponseSchema.parse(data);
    },
    staleTime: 10_000,
    refetchInterval: 15_000,
    ...options,
  });
}

export function useOpsRuns(options?: UseQueryOptions<OpsRunsResponse>) {
  return useQuery({
    queryKey: qk.ops.runs(),
    queryFn: async ({ signal }) => {
      const data = await apiGetJson("/ops/runs", { signal });
      return OpsRunsResponseSchema.parse(data);
    },
    staleTime: 10_000,
    refetchInterval: 30_000,
    ...options,
  });
}
