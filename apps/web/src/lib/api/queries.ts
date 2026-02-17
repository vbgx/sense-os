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

type TopPainQueryParams = {
  limit: number;
  offset: number;
  sort?: string;
  vertical?: string;
  score_min?: number;
  score_max?: number;
  emerging?: boolean;
  tier?: string;
};

function buildQuery(params: Record<string, unknown>) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    qs.set(k, String(v));
  });
  return qs.toString();
}

export function useTopPains(params: TopPainQueryParams) {
  return useQuery({
    queryKey: ["insights", "top_pains", params],
    queryFn: async (): Promise<InsightsTopPains> => {
      const query = buildQuery(params);
      const raw = await fetchJson<unknown>(`/insights/top-pains?${query}`);
      return InsightsTopPainsSchema.parse(raw);
    },
    staleTime: 10_000,
  });
}

export function useClusterDetail(clusterId: string) {
  return useQuery({
    queryKey: ["insights", "cluster_detail", { clusterId }],
    enabled: Boolean(clusterId),
    queryFn: async (): Promise<InsightsClusterDetail> => {
      const raw = await fetchJson<unknown>(
        `/insights/clusters/${encodeURIComponent(clusterId)}`
      );
      return InsightsClusterDetailSchema.parse(raw);
    },
    staleTime: 10_000,
  });
}

export function useEmerging() {
  return useQuery({
    queryKey: ["insights", "emerging"],
    queryFn: async (): Promise<InsightsEmerging> => {
      const raw = await fetchJson<unknown>(`/insights/emerging`);
      return InsightsEmergingSchema.parse(raw);
    },
    staleTime: 10_000,
  });
}

export function useDeclining() {
  return useQuery({
    queryKey: ["insights", "declining"],
    queryFn: async (): Promise<InsightsDeclining> => {
      const raw = await fetchJson<unknown>(`/insights/declining`);
      return InsightsDecliningSchema.parse(raw);
    },
    staleTime: 10_000,
  });
}
