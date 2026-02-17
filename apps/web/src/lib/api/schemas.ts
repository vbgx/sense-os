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
  })
  .passthrough();

export const InsightsTopPainsSchema = z
  .object({
    items: z.array(TopPainItemSchema),
    page: PageSchema.optional(),
    generated_at: ISODateTime.optional(),
  })
  .passthrough();

export const ClusterDetailSchema = z
  .object({
    cluster_id: z.string(),
    title: z.string(),
    summary: z.string().optional(),
    vertical_id: z.string().optional(),
    score: z.number().optional(),
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

export type InsightsTopPains = z.infer<typeof InsightsTopPainsSchema>;
export type InsightsClusterDetail = z.infer<typeof InsightsClusterDetailSchema>;
export type InsightsEmerging = z.infer<typeof InsightsEmergingSchema>;
export type InsightsDeclining = z.infer<typeof InsightsDecliningSchema>;
