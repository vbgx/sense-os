"use client";

import { useQuery } from "@tanstack/react-query";
import {
  TopPainsSchema,
  ClusterDetailSchema,
  VerticalsSchema,
  TrendListResponseSchema,
  OpsQueuesResponseSchema,
  OpsRunsResponseSchema,
} from "@/lib/api/schemas";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

async function apiGetJson(path: string) {
  const url = `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
  const res = await fetch(url, { headers: { Accept: "application/json" } });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status} ${res.statusText}${text ? ` — ${text}` : ""}`);
  }
  return res.json() as Promise<unknown>;
}

/* ──────────────────────────────────────────────────────────
 * INSIGHTS
 * ────────────────────────────────────────────────────────── */

export type TopPainsParams = {
  vertical_id?: string | null;
  tier?: string | null;
  emerging_only?: boolean;
  limit?: number;
  offset?: number;
};

export function useTopPains(params: TopPainsParams) {
  return useQuery({
    queryKey: ["insights", "top_pains", params],
    queryFn: async () => {
      const qs = new URLSearchParams();
      if (params.vertical_id) qs.set("vertical_id", params.vertical_id);
      if (params.tier) qs.set("tier", params.tier);
      if (params.emerging_only) qs.set("emerging_only", "true");
      qs.set("limit", String(params.limit ?? 50));
      qs.set("offset", String(params.offset ?? 0));

      const data = await apiGetJson(`/insights/top_pains?${qs.toString()}`);
      return TopPainsSchema.parse(data);
    },
    staleTime: 30_000,
  });
}

export function useEmerging(params: { vertical_id?: string | null; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["insights", "emerging_opportunities", params],
    queryFn: async () => {
      const qs = new URLSearchParams();
      if (params.vertical_id) qs.set("vertical_id", params.vertical_id);
      qs.set("limit", String(params.limit ?? 50));
      qs.set("offset", String(params.offset ?? 0));

      const data = await apiGetJson(`/insights/emerging_opportunities?${qs.toString()}`);
      return TopPainsSchema.parse(data);
    },
    staleTime: 30_000,
  });
}

export function useDeclining(params: { vertical_id?: string | null; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["insights", "declining_risks", params],
    queryFn: async () => {
      const qs = new URLSearchParams();
      if (params.vertical_id) qs.set("vertical_id", params.vertical_id);
      qs.set("limit", String(params.limit ?? 50));
      qs.set("offset", String(params.offset ?? 0));

      const data = await apiGetJson(`/insights/declining_risks?${qs.toString()}`);
      return TopPainsSchema.parse(data);
    },
    staleTime: 30_000,
  });
}

export function useClusterDetail(cluster_id: string, enabled = true) {
  return useQuery({
    queryKey: ["insights", "cluster_detail", cluster_id],
    queryFn: async () => {
      const data = await apiGetJson(`/insights/${encodeURIComponent(cluster_id)}`);
      return ClusterDetailSchema.parse(data);
    },
    enabled: Boolean(cluster_id) && enabled,
    staleTime: 30_000,
  });
}

/* ──────────────────────────────────────────────────────────
 * VERTICALS
 * ────────────────────────────────────────────────────────── */

export function useVerticals() {
  return useQuery({
    queryKey: ["verticals"],
    queryFn: async () => {
      const data = await apiGetJson("/verticals/");
      return VerticalsSchema.parse(data);
    },
    staleTime: 60_000,
  });
}

/* ──────────────────────────────────────────────────────────
 * TRENDS
 * Endpoint: GET /trending?vertical_id=...
 * ────────────────────────────────────────────────────────── */

export function useTrending(params: {
  vertical_id: number;
  limit?: number;
  offset?: number;
  sparkline_days?: number;
  enabled?: boolean;
}) {
  return useQuery({
    queryKey: ["trending", params],
    queryFn: async () => {
      const qs = new URLSearchParams();
      qs.set("vertical_id", String(params.vertical_id));
      qs.set("limit", String(params.limit ?? 20));
      qs.set("offset", String(params.offset ?? 0));
      qs.set("sparkline_days", String(params.sparkline_days ?? 30));

      const data = await apiGetJson(`/trending?${qs.toString()}`);
      return TrendListResponseSchema.parse(data);
    },
    enabled: params.enabled ?? true,
    staleTime: 30_000,
  });
}

/* ──────────────────────────────────────────────────────────
 * OPS (Transparency)
 * ────────────────────────────────────────────────────────── */

export function useOpsQueues() {
  return useQuery({
    queryKey: ["ops", "queues"],
    queryFn: async () => {
      const data = await apiGetJson("/ops/queues");
      return OpsQueuesResponseSchema.parse(data);
    },
    staleTime: 10_000,
    refetchInterval: 15_000,
  });
}

export function useOpsRuns() {
  return useQuery({
    queryKey: ["ops", "runs"],
    queryFn: async () => {
      const data = await apiGetJson("/ops/runs");
      return OpsRunsResponseSchema.parse(data);
    },
    staleTime: 10_000,
    refetchInterval: 30_000,
  });
}
