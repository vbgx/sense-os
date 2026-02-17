import { z } from "zod";

/* ──────────────────────────────────────────────────────────
 * INSIGHTS — Overview
 * Endpoint: GET /insights/overview
 * ────────────────────────────────────────────────────────── */

export const OverviewKpiSchema = z
  .object({
    label: z.string(),
    value: z.number(),
    delta: z.number().optional(),
    unit: z.string().optional(),
  })
  .passthrough();

export const OverviewBreakoutSchema = z
  .object({
    rank: z.number().int().optional(),
    cluster_id: z.string(),
    vertical_id: z.string().nullable().optional(),

    vertical_label: z.string().nullable().optional(), // optional display
    cluster_summary: z.string().nullable().optional(),

    score: z.number().int().optional(), // optional alias
    breakout_score: z.number().int().optional(),
    exploitability_score: z.number().int().optional(),
    confidence_score: z.number().int().optional(),

    tier: z.string().nullable().optional(),
    status: z.string().nullable().optional(),
    momentum_7d: z.number().optional(),
  })
  .passthrough();

export const OverviewHeatmapCellSchema = z
  .object({
    industry: z.string().optional(),
    function: z.string().optional(),
    density: z.number(),
    top_vertical_id: z.string().nullable().optional(),
    top_label: z.string().nullable().optional(),
  })
  .passthrough();

export const OverviewHeatmapSchema = z
  .object({
    rows: z.array(z.string()).default([]),
    cols: z.array(z.string()).default([]),
    cells: z.array(OverviewHeatmapCellSchema).default([]),
  })
  .passthrough();

export const InsightsOverviewSchema = z
  .object({
    window: z.string().optional(),
    updated_at: z.string().optional(),

    kpis: z.array(OverviewKpiSchema).default([]),
    breakouts: z.array(OverviewBreakoutSchema).default([]),
    heatmap: OverviewHeatmapSchema.optional(),
  })
  .passthrough();

export type OverviewKpi = z.infer<typeof OverviewKpiSchema>;
export type OverviewBreakout = z.infer<typeof OverviewBreakoutSchema>;
export type OverviewHeatmapCell = z.infer<typeof OverviewHeatmapCellSchema>;
export type OverviewHeatmap = z.infer<typeof OverviewHeatmapSchema>;
export type InsightsOverview = z.infer<typeof InsightsOverviewSchema>;
