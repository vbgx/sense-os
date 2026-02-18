import { z } from "zod";

/* ---------------------------------- */
/* Status                             */
/* ---------------------------------- */

export const OverviewStatusSchema = z.enum([
  "hot",
  "emerging",
  "stable",
  "saturated",
  "declining",
]);

export type OverviewStatus = z.infer<typeof OverviewStatusSchema>;

/* ---------------------------------- */
/* KPI                                */
/* ---------------------------------- */

export const OverviewKpiSchema = z
  .object({
    key: z.string().min(1),
    label: z.string().min(1),
    value: z.number().finite(),
    delta_7d: z.number().finite().nullable().optional(),
    sparkline: z.array(z.number().finite()).optional(),
  })
  .strict();

export type OverviewKpi = z.infer<typeof OverviewKpiSchema>;

/* ---------------------------------- */
/* Breakout                           */
/* ---------------------------------- */

export const OverviewBreakoutSchema = z
  .object({
    rank: z.number().int().min(1),
    vertical_id: z.string().min(1),
    vertical_label: z.string().min(1),
    score: z.number().finite(),
    momentum_7d: z.number().finite(),
    confidence: z.number().min(0).max(1),
    tier: z.string().nullable().optional(),
    status: OverviewStatusSchema,
  })
  .strict();

export type OverviewBreakout = z.infer<typeof OverviewBreakoutSchema>;

/* ---------------------------------- */
/* Heatmap                            */
/* ---------------------------------- */

export const OverviewHeatmapCellSchema = z
  .object({
    industry: z.string().min(1),
    function: z.string().min(1),
    value: z.number().finite(),
    top_vertical_id: z.string().nullable().optional(),
    top_vertical_label: z.string().nullable().optional(),
    avg_score: z.number().finite().nullable().optional(),
    momentum_7d: z.number().finite().nullable().optional(),
  })
  .strict();

export type OverviewHeatmapCell = z.infer<typeof OverviewHeatmapCellSchema>;

/* ---------------------------------- */
/* Root                               */
/* ---------------------------------- */

export const OverviewApiSchema = z
  .object({
    updated_at: z.string().datetime(),
    kpis: z.array(OverviewKpiSchema).length(5), // ton design impose 5 KPI
    breakouts: z.array(OverviewBreakoutSchema),
    heatmap: z.array(OverviewHeatmapCellSchema),
  })
  .strict();

export type OverviewApi = z.infer<typeof OverviewApiSchema>;
