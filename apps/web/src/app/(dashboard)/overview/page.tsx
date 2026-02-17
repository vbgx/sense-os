"use client";

import { useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { useInsightsOverview, useTopPains, qk } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";

import { OverviewHeader } from "@/components/overview-v2/OverviewHeader";
import { MarketPulse } from "@/components/overview-v2/MarketPulse";
import { TopBreakoutsTable } from "@/components/overview-v2/TopBreakoutsTable";
import { Heatmap } from "@/components/overview-v2/Heatmap";

export default function Page() {
  const qc = useQueryClient();
  const { state } = useDashboardQueryState();

  const overviewQ = useInsightsOverview({ window: "7d", limit: 10, offset: 0 });

  const topQ = useTopPains({
    limit: 10,
    offset: 0,
    vertical_id: state.vertical_id,
    tier: state.tier,
    emerging_only: state.emerging_only,
  });

  const loading = overviewQ.isLoading || topQ.isLoading;

  const updatedLabel = useMemo(() => {
    const ms = Math.max(overviewQ.dataUpdatedAt ?? 0, topQ.dataUpdatedAt ?? 0);
    return ms ? `Updated ${new Date(ms).toLocaleTimeString()}` : "Updated —";
  }, [overviewQ.dataUpdatedAt, topQ.dataUpdatedAt]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-7 w-[260px]" />
          <Skeleton className="h-4 w-[560px]" />
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <Skeleton className="h-[92px] w-full" />
          <Skeleton className="h-[92px] w-full" />
          <Skeleton className="h-[92px] w-full" />
          <Skeleton className="h-[92px] w-full" />
          <Skeleton className="h-[92px] w-full" />
        </div>
        <Skeleton className="h-[360px] w-full" />
        <Skeleton className="h-[420px] w-full" />
      </div>
    );
  }

  if (overviewQ.isError || topQ.isError) {
    const err =
      (overviewQ.error instanceof Error && overviewQ.error.message) ||
      (topQ.error instanceof Error && topQ.error.message) ||
      "Unknown error";

    return (
      <div className="rounded-2xl border bg-card/40 p-4">
        <div className="text-sm font-semibold">API error</div>
        <div className="mt-1 font-mono text-xs text-muted-foreground">{err}</div>
      </div>
    );
  }

  const overview = overviewQ.data;
  const kpis = overview?.kpis ?? [];

  const breakouts =
    (overview?.breakouts?.length ? overview.breakouts : null) ??
    (topQ.data ?? []).map((it, idx) => ({
      rank: idx + 1,
      cluster_id: it.cluster_id,
      vertical_id: it.vertical_id ?? null,
      vertical_label: it.cluster_summary ?? null,
      cluster_summary: it.cluster_summary ?? null,
      score: it.exploitability_score,
      exploitability_score: it.exploitability_score,
      breakout_score: it.breakout_score,
      confidence_score: it.confidence_score,
      tier: it.exploitability_tier ?? null,
      status: it.opportunity_window_status ?? null,
      momentum_7d: undefined,
    }));

  return (
    <div className="space-y-6">
      <OverviewHeader
        updatedLabel={updatedLabel}
        onRefresh={() => {
          qc.invalidateQueries({
            queryKey: qk.insights.overview({ window: "7d", limit: 10, offset: 0 }),
          });
          qc.invalidateQueries({
            queryKey: qk.insights.topPains({
              limit: 10,
              offset: 0,
              vertical_id: state.vertical_id,
              tier: state.tier,
              emerging_only: state.emerging_only,
            }),
          });
        }}
        isRefreshing={overviewQ.isFetching || topQ.isFetching}
      />

      <MarketPulse kpis={kpis} windowLabel="Window: last 7 days" />

      <TopBreakoutsTable items={breakouts} />

      <Heatmap heatmap={overview?.heatmap} />
    </div>
  );
}
