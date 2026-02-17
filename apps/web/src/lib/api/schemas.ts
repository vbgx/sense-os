import { z } from "zod";

/* ──────────────────────────────────────────────────────────
 * INSIGHTS — Top pains (Opportunity board / Overview / Emerging / Declining)
 * Backend: api_gateway.schemas.insights.TopPainOut
 * ────────────────────────────────────────────────────────── */

export const BuildSignalSchema = z
  .object({
    recommendation: z.string(),
    reasoning_summary: z.string(),
    top_positive_factors: z.array(z.string()).default([]),
    top_risk_factors: z.array(z.string()).default([]),
  })
  .passthrough();

export const TopPainSchema = z
  .object({
    cluster_id: z.string(),
    cluster_summary: z.string().nullable().optional(),

    exploitability_score: z.number().int(),
    exploitability_tier: z.string(),

    severity_score: z.number().int(),
    breakout_score: z.number().int(),
    opportunity_window_status: z.string(),
    confidence_score: z.number().int(),

    dominant_persona: z.string(),
    build_signal: BuildSignalSchema,

    // Optional forward-compat (you may expose these later)
    vertical_id: z.string().nullable().optional(),
    saturation_score: z.number().int().optional(),
    updated_at: z.string().optional(),
  })
  .passthrough();

export const TopPainsSchema = z.array(TopPainSchema);

export type BuildSignal = z.infer<typeof BuildSignalSchema>;
export type TopPain = z.infer<typeof TopPainSchema>;

/* ──────────────────────────────────────────────────────────
 * INSIGHTS — Cluster detail (Deep dive + Inspect drawer)
 * Backend: api_gateway.schemas.cluster_detail.ClusterDetailOut
 * ────────────────────────────────────────────────────────── */

export const TimelinePointSchema = z
  .object({
    date: z.string(), // ISO date (YYYY-MM-DD)
    volume: z.number().int(),
    growth_rate: z.number(),
    velocity: z.number(),
    breakout_flag: z.boolean(),
  })
  .passthrough();

export const RepresentativeSignalSchema = z
  .object({
    id: z.string(),
    text: z.string(),
    // forward-compat (if you expose url/title later)
    url: z.string().optional(),
    title: z.string().optional(),
  })
  .passthrough();

export const ClusterDetailSchema = z
  .object({
    cluster_id: z.string(),
    cluster_summary: z.string().nullable().optional(),

    exploitability_score: z.number().int(),
    exploitability_tier: z.string(),

    exploitability_score_v2: z.number().int(),
    exploitability_tier_v2: z.string(),
    exploitability_version_v2: z.string(),

    severity_score: z.number().int(),
    recurrence_score: z.number().int(),
    monetizability_score: z.number().int(),

    breakout_score: z.number().int(),
    opportunity_window_status: z.string(),
    competitive_heat_score: z.number().int(),
    contradiction_score: z.number().int(),

    confidence_score: z.number().int(),

    key_phrases: z.array(z.string()).default([]),
    representative_signals: z.array(RepresentativeSignalSchema).default([]),
    timeline: z.array(TimelinePointSchema).default([]),
  })
  .passthrough();

export type TimelinePoint = z.infer<typeof TimelinePointSchema>;
export type RepresentativeSignal = z.infer<typeof RepresentativeSignalSchema>;
export type ClusterDetail = z.infer<typeof ClusterDetailSchema>;

/* ──────────────────────────────────────────────────────────
 * VERTICALS
 * Backend: api_gateway.schemas.verticals.VerticalOut (unknown shape)
 * ────────────────────────────────────────────────────────── */

export const VerticalSchema = z
  .object({
    id: z.union([z.number().int(), z.string()]),
    name: z.string(),
  })
  .passthrough();

export const VerticalsSchema = z.array(VerticalSchema);

export type Vertical = z.infer<typeof VerticalSchema>;

/* ──────────────────────────────────────────────────────────
 * TRENDS
 * Backend: api_gateway.schemas.trends.TrendListResponse (unknown shape)
 * We keep it permissive but typed, no any.
 * ────────────────────────────────────────────────────────── */

export const TrendSparkPointSchema = z
  .object({
    date: z.string().optional(),
    value: z.number().optional(),
    volume: z.number().optional(),
    velocity: z.number().optional(),
    breakout_flag: z.boolean().optional(),
  })
  .strict();

export const TrendItemSchema = z
  .object({
    cluster_id: z.string(),
    cluster_summary: z.string().nullable().optional(),

    exploitability_score: z.number().int().optional(),
    breakout_score: z.number().int().optional(),

    sparkline: z.array(TrendSparkPointSchema).default([]),
  })
  .passthrough();

export const TrendListResponseSchema = z
  .object({
    items: z.array(TrendItemSchema).default([]),
  })
  .passthrough();

export type TrendSparkPoint = z.infer<typeof TrendSparkPointSchema>;
export type TrendItem = z.infer<typeof TrendItemSchema>;
export type TrendListResponse = z.infer<typeof TrendListResponseSchema>;

/* ──────────────────────────────────────────────────────────
 * OPS (Analytics / Transparency)
 * Backend: /ops/queues + /ops/runs (unknown shape)
 * ────────────────────────────────────────────────────────── */

export const OpsQueueItemSchema = z
  .object({
    name: z.string().optional(),
    depth: z.number().int().optional(),
    lag_seconds: z.number().optional(),
    oldest_age_seconds: z.number().optional(),
  })
  .passthrough();

export const OpsQueuesResponseSchema = z
  .object({
    items: z.array(OpsQueueItemSchema).default([]),
  })
  .passthrough();

export type OpsQueueItem = z.infer<typeof OpsQueueItemSchema>;
export type OpsQueuesResponse = z.infer<typeof OpsQueuesResponseSchema>;

export const OpsRunItemSchema = z
  .object({
    run_id: z.string().optional(),
    id: z.string().optional(),
    status: z.string().optional(),
    started_at: z.string().optional(),
    finished_at: z.string().optional(),
    day: z.string().optional(),
    vertical_id: z.number().int().optional(),
  })
  .passthrough();

export const OpsRunsResponseSchema = z
  .object({
    items: z.array(OpsRunItemSchema).default([]),
  })
  .passthrough();

export type OpsRunItem = z.infer<typeof OpsRunItemSchema>;
export type OpsRunsResponse = z.infer<typeof OpsRunsResponseSchema>;
