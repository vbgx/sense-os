import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "@/lib/api/client";
import {
  InsightsTopPainsSchema,
  InsightsClusterDetailSchema,
  InsightsEmergingSchema,
  InsightsDecliningSchema,
  type InsightsTopPains,
  type InsightsClusterDetail,
  type InsightsEmerging,
  type InsightsDeclining,
} from "@/lib/api/schemas";

function parseOrThrow<T>(schema: { parse: (x: unknown) => T }, payload: unknown): T {
  return schema.parse(payload);
}

export function useTopPains(params?: { limit?: number; offset?: number }) {
  const limit = params?.limit ?? 25;
  const offset = params?.offset ?? 0;

  return useQuery({
    queryKey: ["insights", "top_pains", { limit, offset }],
    queryFn: async (): Promise<InsightsTopPains> => {
      const raw = await fetchJson<unknown>(`/insights/top-pains?limit=${limit}&offset=${offset}`);
      return parseOrThrow(InsightsTopPainsSchema, raw);
    },
    staleTime: 15_000,
  });
}

export function useClusterDetail(clusterId: string) {
  return useQuery({
    queryKey: ["insights", "cluster_detail", { clusterId }],
    enabled: Boolean(clusterId),
    queryFn: async (): Promise<InsightsClusterDetail> => {
      const raw = await fetchJson<unknown>(`/insights/clusters/${encodeURIComponent(clusterId)}`);
      return parseOrThrow(InsightsClusterDetailSchema, raw);
    },
    staleTime: 15_000,
  });
}

export function useEmerging() {
  return useQuery({
    queryKey: ["insights", "emerging"],
    queryFn: async (): Promise<InsightsEmerging> => {
      const raw = await fetchJson<unknown>(`/insights/emerging`);
      return parseOrThrow(InsightsEmergingSchema, raw);
    },
    staleTime: 15_000,
  });
}

export function useDeclining() {
  return useQuery({
    queryKey: ["insights", "declining"],
    queryFn: async (): Promise<InsightsDeclining> => {
      const raw = await fetchJson<unknown>(`/insights/declining`);
      return parseOrThrow(InsightsDecliningSchema, raw);
    },
    staleTime: 15_000,
  });
}
