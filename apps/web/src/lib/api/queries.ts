import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import { fetchJson } from "./client";
import { OverviewApiSchema, type OverviewApi } from "./overview.schemas";

/**
 * GOAL:
 * - make all pages compile again (strict TS)
 * - keep Zod validation (but not over-fragile)
 * - support the params your pages already pass
 */

// -----------------------------
// Shared helpers
// -----------------------------
function qs(params?: Record<string, unknown>): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null) continue;
    sp.set(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

// -----------------------------
// TopPain (must match what your UI/components expect)
// IMPORTANT: dominant_persona must be a string (not nullable) because UI types assume string.
// We normalize null/undefined -> "".
// -----------------------------
export const TopPainSchema = z
  .object({
    cluster_id: z.string(),

    // identity / labels
    vertical_id: z.string().nullable().optional(),
    vertical_label: z.string().nullable().optional(),
    cluster_summary: z.string().nullable().optional(),

    // required by OpportunityTable / various pages
    exploitability_score: z.number(),
    exploitability_tier: z.string(),
    severity_score: z.number(),
    breakout_score: z.number(),
    opportunity_window_status: z.string(),
    confidence_score: z.number(),

    // used in filtering / command palette (normalize to string)
    dominant_persona: z.string().optional().default(""),
    build_signal: z.unknown().nullable().optional(),

    // optional extras used across pages
    saturation_score: z.number().nullable().optional(),
    momentum_7d: z.number().nullable().optional(),
    tier: z.string().nullable().optional(),
    status: z.string().nullable().optional(),
    updated_at: z.string().optional(),
  })
  .passthrough()
  .transform((x) => ({
    ...x,
    dominant_persona: typeof (x as any).dominant_persona === "string" ? (x as any).dominant_persona : "",
  }));

export type TopPain = z.infer<typeof TopPainSchema>;
export const TopPainListSchema = z.array(TopPainSchema);

// -----------------------------
// Other schemas (keep permissive for now)
// -----------------------------
export const ClusterDetailSchema = z.any();
export type ClusterDetail = z.infer<typeof ClusterDetailSchema>;

export const VerticalSchema = z.any();
export type Vertical = z.infer<typeof VerticalSchema>;

// --- Ops responses used by analytics page ---
export const OpsQueuesResponseSchema = z.object({ items: z.array(z.any()) }).passthrough();
export type OpsQueuesResponse = z.infer<typeof OpsQueuesResponseSchema>;

export const OpsRunsResponseSchema = z.object({ items: z.array(z.any()) }).passthrough();
export type OpsRunsResponse = z.infer<typeof OpsRunsResponseSchema>;

// --- Trends response used by vertical deep dive ---
// UI expects TrendItem has sparkline: TrendSparkPoint[] (required in your schemas.ts).
// We normalize missing sparkline -> [].
const TrendItemCompatSchema = TopPainSchema.extend({
  sparkline: z.array(z.any()).optional().default([]),
}).transform((x) => ({
  ...x,
  sparkline: Array.isArray((x as any).sparkline) ? (x as any).sparkline : [],
}));

export const TrendListResponseSchema = z
  .object({ items: z.array(TrendItemCompatSchema) })
  .passthrough()
  .transform((x) => ({
    ...x,
    items: Array.isArray((x as any).items) ? (x as any).items : [],
  }));

export type TrendListResponse = z.infer<typeof TrendListResponseSchema>;

// -----------------------------
// Query keys
// -----------------------------
export const qk = {
  overview: ["overview"] as const,

  meta: {
    status: () => ["meta", "status"] as const,
  },

  topPains: (params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }) =>
    ["insights", "top_pains", params?.vertical_id ?? "all", params?.tier ?? "all", params?.limit ?? 50, params?.offset ?? 0] as const,

  emerging: (params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }) =>
    ["insights", "emerging_opportunities", params?.vertical_id ?? "all", params?.tier ?? "all", params?.limit ?? 200, params?.offset ?? 0] as const,

  declining: (params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }) =>
    ["insights", "declining_risks", params?.vertical_id ?? "all", params?.tier ?? "all", params?.limit ?? 200, params?.offset ?? 0] as const,

  clusterDetail: (clusterId: string) => ["insights", "cluster_detail", clusterId] as const,

  verticals: () => ["verticals"] as const,

  trending: (params?: { vertical_id?: string | number; limit?: number; offset?: number; sparkline_days?: number }) =>
    ["trends", "trending", params?.vertical_id ?? "all", params?.sparkline_days ?? 30, params?.limit ?? 50, params?.offset ?? 0] as const,

  opsQueues: () => ["ops", "queues"] as const,
  opsRuns: () => ["ops", "runs"] as const,
};

// -----------------------------
// API functions
// -----------------------------
export async function getOverview(): Promise<OverviewApi> {
  const raw = await fetchJson<unknown>("/overview");
  return OverviewApiSchema.parse(raw);
}

export async function getTopPains(params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }): Promise<TopPain[]> {
  // backend currently may ignore tier; keep it as frontend-only filter param for now
  const { tier: _tier, ...rest } = params ?? {};
  const raw = await fetchJson<unknown>(`/insights/top_pains${qs(rest)}`);
  const parsed = TopPainListSchema.parse(raw);
  if (!_tier) return parsed;
  return parsed.filter((x) => (x.tier ?? "").toLowerCase() === String(_tier).toLowerCase());
}

export async function getEmerging(params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }): Promise<TopPain[]> {
  const { tier: _tier, ...rest } = params ?? {};
  const raw = await fetchJson<unknown>(`/insights/emerging_opportunities${qs(rest)}`);
  const parsed = TopPainListSchema.parse(raw);
  if (!_tier) return parsed;
  return parsed.filter((x) => (x.tier ?? "").toLowerCase() === String(_tier).toLowerCase());
}

export async function getDeclining(params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }): Promise<TopPain[]> {
  const { tier: _tier, ...rest } = params ?? {};
  const raw = await fetchJson<unknown>(`/insights/declining_risks${qs(rest)}`);
  const parsed = TopPainListSchema.parse(raw);
  if (!_tier) return parsed;
  return parsed.filter((x) => (x.tier ?? "").toLowerCase() === String(_tier).toLowerCase());
}

export async function getClusterDetail(clusterId: string): Promise<ClusterDetail> {
  const raw = await fetchJson<unknown>(`/insights/${encodeURIComponent(clusterId)}`);
  return ClusterDetailSchema.parse(raw);
}

export async function getVerticals(): Promise<Vertical[]> {
  const raw = await fetchJson<unknown>("/verticals/");
  return z.array(VerticalSchema).parse(raw);
}

export async function getTrending(params?: { vertical_id?: string | number; limit?: number; offset?: number; sparkline_days?: number }): Promise<TrendListResponse> {
  // backend might not support sparkline_days yet; send it anyway (harmless if ignored)
  const raw = await fetchJson<unknown>(`/trends/trending${qs(params)}`);
  return TrendListResponseSchema.parse(raw);
}

export async function getOpsQueues(): Promise<OpsQueuesResponse> {
  const raw = await fetchJson<unknown>("/ops/queues");
  return OpsQueuesResponseSchema.parse(raw);
}

export async function getOpsRuns(): Promise<OpsRunsResponse> {
  const raw = await fetchJson<unknown>("/ops/runs");
  return OpsRunsResponseSchema.parse(raw);
}

// -----------------------------
// Hooks
// -----------------------------
export function useOverview() {
  return useQuery({ queryKey: qk.overview, queryFn: getOverview });
}

export function useTopPains(params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }) {
  return useQuery({ queryKey: qk.topPains(params), queryFn: () => getTopPains(params) });
}

export function useEmerging(params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }) {
  return useQuery({ queryKey: qk.emerging(params), queryFn: () => getEmerging(params) });
}

export function useDeclining(params?: { limit?: number; offset?: number; vertical_id?: string | number; tier?: string | null }) {
  return useQuery({ queryKey: qk.declining(params), queryFn: () => getDeclining(params) });
}

/**
 * Backward-compat with old call sites:
 * useClusterDetail(clusterId, enabled)
 */
export function useClusterDetail(clusterId: string, enabled?: boolean) {
  return useQuery({
    queryKey: qk.clusterDetail(clusterId),
    queryFn: () => getClusterDetail(clusterId),
    enabled: enabled ?? Boolean(clusterId),
  });
}

export function useVerticals() {
  return useQuery({ queryKey: qk.verticals(), queryFn: getVerticals });
}

/**
 * Old call sites pass:
 * useTrending({ vertical_id, limit, offset, sparkline_days, enabled })
 */
export function useTrending(params?: {
  vertical_id?: string | number;
  limit?: number;
  offset?: number;
  sparkline_days?: number;
  enabled?: boolean;
}) {
  const { enabled, ...rest } = params ?? {};
  return useQuery({
    queryKey: qk.trending(rest),
    queryFn: () => getTrending(rest),
    enabled: enabled ?? true,
  });
}

export function useOpsQueues() {
  return useQuery({ queryKey: qk.opsQueues(), queryFn: getOpsQueues });
}

export function useOpsRuns() {
  return useQuery({ queryKey: qk.opsRuns(), queryFn: getOpsRuns });
}