import { z } from "zod";

export const DateOnly = z
  .string()
  .refine((s) => /^\d{4}-\d{2}-\d{2}$/.test(s), "Invalid date (expected YYYY-MM-DD)");

export const TimelinePointSchema = z
  .object({
    date: DateOnly,
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
  })
  .passthrough();

/**
 * ClusterDetailOut (Pydantic)
 * response: GET /insights/{cluster_id}
 */
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

    key_phrases: z.array(z.string()),
    representative_signals: z.array(RepresentativeSignalSchema),
    timeline: z.array(TimelinePointSchema),
  })
  .passthrough();

export type ClusterDetail = z.infer<typeof ClusterDetailSchema>;
export type TimelinePoint = z.infer<typeof TimelinePointSchema>;
export type RepresentativeSignal = z.infer<typeof RepresentativeSignalSchema>;

/**
 * TopPainOut (Pydantic)
 * response: GET /insights/top_pains (and emerging/declining lists)
 */
export const BuildSignalSchema = z
  .object({
    // BuildSignalOut exists in your API gateway; keep flexible but typed enough to render safely.
    // Add fields later if you want to display them.
  })
  .passthrough();

export const TopPainSchema = z
  .object({
    cluster_id: z.string(),
    vertical_id: z.string().nullable().optional(),
    cluster_summary: z.string().nullable().optional(),

    exploitability_score: z.number().int(),
    exploitability_tier: z.string(),
    severity_score: z.number().int(),

    breakout_score: z.number().int(),
    saturation_score: z.number().int(),

    opportunity_window_status: z.string(),
    confidence_score: z.number().int(),
    dominant_persona: z.string(),

    build_signal: BuildSignalSchema,
  })
  .passthrough();

export const TopPainsSchema = z.array(TopPainSchema);

export type TopPain = z.infer<typeof TopPainSchema>;
export type TopPains = z.infer<typeof TopPainsSchema>;
