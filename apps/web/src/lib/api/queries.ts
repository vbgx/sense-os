import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "@/lib/api/client";
import {
  TopPainsSchema,
  ClusterDetailSchema,
  type TopPains,
  type ClusterDetail,
} from "@/lib/api/schemas";

type TopPainsParams = {
  vertical_id?: string;
  tier?: string;
  emerging_only?: boolean;
  limit: number;
  offset: number;
};

function buildQuery(params: Record<string, unknown>) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    qs.set(k, String(v));
  });
  return qs.toString();
}

export function useTopPains(params: TopPainsParams) {
  return useQuery({
    queryKey: ["insights", "top_pains", params],
    queryFn: async (): Promise<TopPains> => {
      const query = buildQuery(params);
      const raw = await fetchJson<unknown>(`/insights/top_pains?${query}`);
      return TopPainsSchema.parse(raw);
    },
    staleTime: 10_000,
  });
}

export function useEmerging(params: { vertical_id?: string; limit: number; offset: number }) {
  return useQuery({
    queryKey: ["insights", "emerging_opportunities", params],
    queryFn: async (): Promise<TopPains> => {
      const query = buildQuery(params);
      const raw = await fetchJson<unknown>(`/insights/emerging_opportunities?${query}`);
      return TopPainsSchema.parse(raw);
    },
    staleTime: 10_000,
  });
}

export function useDeclining(params: { vertical_id?: string; limit: number; offset: number }) {
  return useQuery({
    queryKey: ["insights", "declining_risks", params],
    queryFn: async (): Promise<TopPains> => {
      const query = buildQuery(params);
      const raw = await fetchJson<unknown>(`/insights/declining_risks?${query}`);
      return TopPainsSchema.parse(raw);
    },
    staleTime: 10_000,
  });
}

export function useClusterDetail(clusterId: string) {
  return useQuery({
    queryKey: ["insights", "cluster_detail", { clusterId }],
    enabled: Boolean(clusterId),
    queryFn: async (): Promise<ClusterDetail> => {
      const raw = await fetchJson<unknown>(`/insights/${encodeURIComponent(clusterId)}`);
      return ClusterDetailSchema.parse(raw);
    },
    staleTime: 10_000,
  });
}
