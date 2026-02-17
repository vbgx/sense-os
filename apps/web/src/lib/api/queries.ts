import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "@/lib/api/client";
import {
  InsightsTopPainsSchema,
  type InsightsTopPains,
} from "@/lib/api/schemas";

type TopPainQueryParams = {
  limit: number;
  offset: number;
  sort?: string;
  vertical?: string;
  score_min?: number;
  score_max?: number;
  emerging?: boolean;
};

function buildQuery(params: TopPainQueryParams) {
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
