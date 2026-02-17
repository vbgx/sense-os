import { z } from "zod";

export const ISODateTime = z
  .string()
  .refine((s) => !Number.isNaN(Date.parse(s)), "Invalid datetime string");

export const PageSchema = z
  .object({
    limit: z.number().int().nonnegative(),
    offset: z.number().int().nonnegative(),
    total: z.number().int().nonnegative().optional(),
  })
  .passthrough();

export const TopPainItemSchema = z
  .object({
    cluster_id: z.string(),
    title: z.string(),
    score: z.number(),
    vertical_id: z.string().optional(),
    updated_at: ISODateTime.optional(),

    exploitability: z.number().optional(),
    growth: z.number().optional(),
    severity: z.number().optional(),
    underserved: z.number().optional(),
    confidence: z.number().optional(),
    persona: z.string().optional(),
    tier: z.string().optional(),
    emerging: z.boolean().optional(),
  })
  .passthrough();

export const InsightsTopPainsSchema = z
  .object({
    items: z.array(TopPainItemSchema),
    page: PageSchema.optional(),
    generated_at: ISODateTime.optional(),
  })
  .passthrough();

export const RepresentativeSignalSchema = z
  .object({
    id: z.string().optional(),
    title: z.string().optional(),
    url: z.string().url().optional(),
    source: z.string().optional(),
    created_at: ISODateTime.optional(),
    score: z.number().optional(),
    text: z.string().optional(),
  })
  .passthrough();

export const ClusterDetailSchema = z
  .object({
    cluster_id: z.string(),
    title: z.string(),
    summary: z.string().optional(),
    vertical_id: z.string().optional(),
    score: z.number().optional(),

    key_phrases: z.array(z.string()).optional(),
    representative_signals: z.array(RepresentativeSignalSchema).optional(),
    scores: z
      .object({
        exploitability: z.number().optional(),
        growth: z.number().optional(),
        severity: z.number().optional(),
        underserved: z.number().optional(),
        confidence: z.number().optional(),
      })
      .optional(),
  })
  .passthrough();

export const InsightsClusterDetailSchema = z
  .object({
    item: ClusterDetailSchema,
    generated_at: ISODateTime.optional(),
  })
  .passthrough();

export const TrendItemSchema = z
  .object({
    cluster_id: z.string(),
    title: z.string(),
    score: z.number().optional(),
    velocity: z.number().optional(),
    breakout_score: z.number().optional(),
    declining_score: z.number().optional(),
    vertical_id: z.string().optional(),
  })
  .passthrough();

export const InsightsEmergingSchema = z
  .object({
    items: z.array(TrendItemSchema),
    generated_at: ISODateTime.optional(),
  })
  .passthrough();

export const InsightsDecliningSchema = z
  .object({
    items: z.array(TrendItemSchema),
    generated_at: ISODateTime.optional(),
  })
  .passthrough();

export type TopPainItem = z.infer<typeof TopPainItemSchema>;
export type InsightsTopPains = z.infer<typeof InsightsTopPainsSchema>;
export type ClusterDetail = z.infer<typeof ClusterDetailSchema>;
export type InsightsClusterDetail = z.infer<typeof InsightsClusterDetailSchema>;
export type InsightsEmerging = z.infer<typeof InsightsEmergingSchema>;
export type InsightsDeclining = z.infer<typeof InsightsDecliningSchema>;
