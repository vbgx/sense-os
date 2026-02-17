"use client";

import { useMemo, type ComponentProps } from "react";
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

  const updatedLabel = useMemo(() => {
    const ms = Math.max(overviewQ.dataUpdatedAt ?? 0, topQ.dataUpdatedAt ?? 0);
    return ms ? `Updated ${new Date(ms).toLocaleTimeString()}` : "Updated —";
  }, [overviewQ.dataUpdatedAt, topQ.dataUpdatedAt]);

  const overview = overviewQ.data;

  // ---- KPI adapter (backend -> MarketKpi) ----
  const kpis = useMemo(() => {
    const raw = (overview as unknown as { kpis?: unknown[] } | undefined)?.kpis;
    if (!Array.isArray(raw)) return [];

    return raw
      .map((it, idx) => {
        const o = it as Record<string, unknown>;

        const key = typeof o.key === "string" && o.key.trim().length ? o.key : `kpi_${idx}`;
        const label = typeof o.label === "string" && o.label.trim().length ? o.label : key;

        const value =
          typeof o.value === "string"
            ? o.value
            : typeof o.value === "number"
              ? String(o.value)
              : "—";

        const delta_7d =
          typeof o.delta_7d === "number"
            ? o.delta_7d
            : typeof o.delta === "number"
              ? o.delta
              : null;

        const badge = typeof o.badge === "string" ? o.badge : null;
        const note = typeof o.note === "string" ? o.note : null;

        return { key, label, value, delta_7d, badge, note };
      })
      .filter((k) => k.key.length > 0);
  }, [overview]);

  // ---- Breakouts source (prefer overview.breakouts, fallback top pains) ----
  const breakouts = useMemo(() => {
    if (overview?.breakouts?.length) return overview.breakouts;

    return (topQ.data ?? []).map((it, idx) => ({
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
  }, [overview, topQ.data]);

  // ---- Heatmap adapter (backend -> HeatmapData) ----
  const heatmap = useMemo<ComponentProps<typeof Heatmap>["heatmap"]>(() => {
    const hm = (overview as unknown as { heatmap?: unknown } | undefined)?.heatmap;
    if (!hm || typeof hm !== "object") return null;

    const o = hm as Record<string, unknown>;

    const rowsRaw = Array.isArray(o.rows) ? o.rows : [];
    const colsRaw = Array.isArray(o.cols) ? o.cols : [];
    const cellsRaw = Array.isArray(o.cells) ? o.cells : [];

    const rows = rowsRaw.filter((x): x is string => typeof x === "string" && x.length > 0);
    const cols = colsRaw.filter((x): x is string => typeof x === "string" && x.length > 0);

    type BackendCell = {
      industry?: string;
      function?: string;
      density?: number;
    };

    const backendCells: BackendCell[] = cellsRaw
      .map((it) => (it && typeof it === "object" ? (it as Record<string, unknown>) : null))
      .filter((it): it is Record<string, unknown> => !!it)
      .map((it) => ({
        industry: typeof it.industry === "string" ? it.industry : undefined,
        function: typeof it.function === "string" ? it.function : undefined,
        density: typeof it.density === "number" ? it.density : undefined,
      }));

    const lookup = new Map<string, BackendCell>();
    for (const c of backendCells) {
      if (!c.industry || !c.function) continue;
      lookup.set(`${c.industry}::${c.function}`, c);
    }

    const rowObjects = rows.map((r) => ({
      row: r,
      cells: cols.map((c) => {
        const hit = lookup.get(`${r}::${c}`);
        const value = typeof hit?.density === "number" ? hit.density : 0;
        return { col: c, value };
      }),
    }));

    return { rows: rowObjects, cols };
  }, [overview]);

  const loading = overviewQ.isLoading || topQ.isLoading;

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

      <Heatmap heatmap={heatmap} />
    </div>
  );
}
