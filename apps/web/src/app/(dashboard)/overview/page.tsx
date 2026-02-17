"use client";

import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { useDeclining, useEmerging, useTopPains } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";
import { KpiRow } from "@/components/overview/KpiRow";
import { Highlights } from "@/components/overview/Highlights";
import { TopOpportunities } from "@/components/overview/TopOpportunities";

function pct(part: number, total: number) {
  if (total <= 0) return 0;
  return part / total;
}

export default function Page() {
  const { state } = useDashboardQueryState();

  const topQ = useTopPains({
    limit: 50,
    offset: 0,
    vertical_id: state.vertical_id,
    tier: state.tier,
    emerging_only: state.emerging_only,
  });

  const emergingQ = useEmerging({
    limit: 50,
    offset: 0,
    vertical_id: state.vertical_id,
  });

  const decliningQ = useDeclining({
    limit: 50,
    offset: 0,
    vertical_id: state.vertical_id,
  });

  const loading = topQ.isLoading || emergingQ.isLoading || decliningQ.isLoading;

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <div className="text-xl font-semibold">Overview</div>
          <div className="mt-1 text-sm text-muted-foreground">Market snapshot</div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Skeleton className="h-[74px] w-full" />
          <Skeleton className="h-[74px] w-full" />
          <Skeleton className="h-[74px] w-full" />
          <Skeleton className="h-[74px] w-full" />
        </div>

        <Skeleton className="h-[180px] w-full" />
        <Skeleton className="h-[420px] w-full" />
      </div>
    );
  }

  if (topQ.isError || emergingQ.isError || decliningQ.isError) {
    const err =
      (topQ.error instanceof Error && topQ.error.message) ||
      (emergingQ.error instanceof Error && emergingQ.error.message) ||
      (decliningQ.error instanceof Error && decliningQ.error.message) ||
      "Unknown error";

    return (
      <div className="rounded-md border p-3">
        <div className="text-sm font-medium">API error</div>
        <div className="mt-1 text-xs text-muted-foreground">{err}</div>
      </div>
    );
  }

  const top = topQ.data ?? [];
  const emerging = emergingQ.data ?? [];
  const declining = decliningQ.data ?? [];

  const surfaced = top.length;

  const avgExploitability =
    top.length === 0
      ? 0
      : top.reduce((sum, it) => sum + it.exploitability_score, 0) / top.length;

  const emergingPct = pct(emerging.length, Math.max(1, surfaced));
  const decliningPct = pct(declining.length, Math.max(1, surfaced));

  const lastUpdatedMs = Math.max(topQ.dataUpdatedAt, emergingQ.dataUpdatedAt, decliningQ.dataUpdatedAt);
  const lastUpdated = lastUpdatedMs ? new Date(lastUpdatedMs).toLocaleString() : "—";

  return (
    <div className="space-y-6">
      <div>
        <div className="text-xl font-semibold">Overview</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Market snapshot • last refreshed: {lastUpdated}
        </div>
      </div>

      <KpiRow
        clustersSurfaced={surfaced}
        emergingPct={emergingPct}
        decliningPct={decliningPct}
        avgExploitability={avgExploitability}
      />

      <Highlights top={top} emerging={emerging} declining={declining} />

      <TopOpportunities items={top} />
    </div>
  );
}
