"use client";

import { useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { useInsightsOverview, useTopPains, qk } from "@/lib/api/queries";
import { getErrorMessage } from "@/lib/utils/getErrorMessage";

import { OverviewHeader } from "@/components/overview-v2/OverviewHeader";
import { MarketPulse, type MarketKpi } from "@/components/overview-v2/MarketPulse";
import { TopBreakoutsTable, type BreakoutItem } from "@/components/overview-v2/TopBreakoutsTable";
import { Heatmap, type HeatmapData, type HeatmapRow, type HeatmapCell } from "@/components/overview-v2/Heatmap";

function clampText(s: string, max = 180) {
  const t = s.trim();
  return t.length > max ? `${t.slice(0, max)}…` : t;
}

function isObj(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null;
}

function getStr(o: Record<string, unknown>, k: string): string | null {
  const v = o[k];
  return typeof v === "string" ? v : null;
}

function getNum(o: Record<string, unknown>, k: string): number | null {
  const v = o[k];
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

const MOCK_KPIS: MarketKpi[] = [
  { key: "active_verticals", label: "Total Active Verticals", value: "—", delta_7d: null, badge: "active", note: "Waiting for data" },
  { key: "emerging_7d", label: "Emerging Clusters (7d)", value: "—", delta_7d: null, badge: "new", note: "Waiting for data" },
  { key: "declining", label: "Declining Clusters", value: "—", delta_7d: null, badge: "down", note: "Waiting for data" },
  { key: "volatility", label: "Opportunity Volatility Index", value: "—", delta_7d: null, badge: "risk", note: "Waiting for data" },
  { key: "signal_growth", label: "Signal Growth", value: "—", delta_7d: null, badge: "7d", note: "Waiting for data" },
];

const MOCK_BREAKOUTS: BreakoutItem[] = Array.from({ length: 5 }).map((_, idx) => ({
  rank: idx + 1,
  cluster_id: `mock_${idx + 1}`,
  vertical_id: null,
  vertical_label: "—",
  cluster_summary: "Waiting for breakouts…",
  score: null,
  breakout_score: null,
  exploitability_score: null,
  confidence_score: null,
  tier: "—",
  status: "stable",
  momentum_7d: null,
}));

const MOCK_HEATMAP: HeatmapData = {
  cols: ["Ops", "Engineering", "Growth", "Finance", "People"],
  rows: [
    {
      row: "Healthcare",
      cells: [
        { col: "Ops", value: 0.84, top_label: "ops core", top_vertical_id: null },
        { col: "Engineering", value: 0.62, top_label: "compliance tools", top_vertical_id: null },
        { col: "Growth", value: 0.41, top_label: "acquisition ops", top_vertical_id: null },
        { col: "Finance", value: 0.19, top_label: "few signals", top_vertical_id: null },
        { col: "People", value: 0.36, top_label: "hiring friction", top_vertical_id: null },
      ],
    },
    {
      row: "DevTools",
      cells: [
        { col: "Ops", value: 0.33, top_label: "ops enablement", top_vertical_id: null },
        { col: "Engineering", value: 0.87, top_label: "CI/CD security", top_vertical_id: null },
        { col: "Growth", value: 0.58, top_label: "dev marketing", top_vertical_id: null },
        { col: "Finance", value: 0.22, top_label: "finops", top_vertical_id: null },
        { col: "People", value: 0.18, top_label: "teams", top_vertical_id: null },
      ],
    },
    {
      row: "Finance",
      cells: [
        { col: "Ops", value: 0.55, top_label: "ar automation", top_vertical_id: null },
        { col: "Engineering", value: 0.39, top_label: "infra", top_vertical_id: null },
        { col: "Growth", value: 0.36, top_label: "distribution", top_vertical_id: null },
        { col: "Finance", value: 0.71, top_label: "finops", top_vertical_id: null },
        { col: "People", value: 0.24, top_label: "people ops", top_vertical_id: null },
      ],
    },
  ],
};

function normalizeKpis(overview: unknown): MarketKpi[] {
  if (!isObj(overview)) return MOCK_KPIS;
  const raw = overview.kpis;
  if (!Array.isArray(raw) || raw.length === 0) return MOCK_KPIS;

  const out: MarketKpi[] = [];
  for (let i = 0; i < raw.length; i++) {
    const x = raw[i];
    if (!isObj(x)) continue;

    const key = getStr(x, "key") ?? `kpi_${i}`;
    const label = getStr(x, "label") ?? "—";

    const valueRaw = x.value;
    const value =
      typeof valueRaw === "string"
        ? valueRaw
        : typeof valueRaw === "number"
          ? String(valueRaw)
          : valueRaw === null || valueRaw === undefined
            ? "—"
            : String(valueRaw);

    const deltaRaw = x.delta_7d;
    const delta_7d =
      typeof deltaRaw === "number" && Number.isFinite(deltaRaw) ? deltaRaw : deltaRaw === null ? null : null;

    const badge = getStr(x, "badge");
    const note = getStr(x, "note");

    out.push({
      key,
      label,
      value,
      delta_7d,
      badge: badge ?? null,
      note: note ?? null,
    });
  }

  return out.length ? out : MOCK_KPIS;
}

function normalizeBreakoutsFromOverview(overview: unknown): BreakoutItem[] | null {
  if (!isObj(overview)) return null;
  const raw = overview.breakouts;
  if (!Array.isArray(raw) || raw.length === 0) return null;

  const out: BreakoutItem[] = [];
  for (let i = 0; i < raw.length; i++) {
    const it = raw[i];
    if (!isObj(it)) continue;

    const cluster_id = getStr(it, "cluster_id") ?? `cluster_${i + 1}`;
    const rank = getNum(it, "rank") ?? i + 1;

    out.push({
      rank,
      cluster_id,
      vertical_id: getStr(it, "vertical_id"),
      vertical_label: getStr(it, "vertical_label"),
      cluster_summary: getStr(it, "cluster_summary"),
      score: getNum(it, "score"),
      breakout_score: getNum(it, "breakout_score"),
      exploitability_score: getNum(it, "exploitability_score"),
      confidence_score: getNum(it, "confidence_score"),
      tier: getStr(it, "tier"),
      status: getStr(it, "status"),
      momentum_7d: getNum(it, "momentum_7d"),
    });
  }

  return out.length ? out : null;
}

function normalizeBreakoutsFromTopPains(top: unknown): BreakoutItem[] | null {
  if (!Array.isArray(top) || top.length === 0) return null;

  const out: BreakoutItem[] = [];
  for (let i = 0; i < top.length; i++) {
    const it = top[i];
    if (!isObj(it)) continue;

    const cluster_id = getStr(it, "cluster_id") ?? "";
    if (!cluster_id) continue;

    out.push({
      rank: i + 1,
      cluster_id,
      vertical_id: getStr(it, "vertical_id"),
      vertical_label: getStr(it, "cluster_summary"),
      cluster_summary: getStr(it, "cluster_summary"),
      score: getNum(it, "exploitability_score"),
      breakout_score: getNum(it, "breakout_score"),
      exploitability_score: getNum(it, "exploitability_score"),
      confidence_score: getNum(it, "confidence_score"),
      tier: getStr(it, "exploitability_tier"),
      status: getStr(it, "opportunity_window_status"),
      momentum_7d: null,
    });
  }

  return out.length ? out : null;
}

function normalizeHeatmap(overview: unknown): HeatmapData {
  if (!isObj(overview)) return MOCK_HEATMAP;

  const h = overview.heatmap;
  if (!isObj(h)) return MOCK_HEATMAP;

  const colsRaw = h.cols;
  const rowsRaw = h.rows;

  if (!Array.isArray(colsRaw) || !Array.isArray(rowsRaw)) return MOCK_HEATMAP;

  const cols = colsRaw.filter((c): c is string => typeof c === "string" && c.length > 0);
  if (cols.length === 0) return MOCK_HEATMAP;

  const rows: HeatmapRow[] = [];
  for (const r of rowsRaw) {
    if (!isObj(r)) continue;
    const row = getStr(r, "row");
    const cellsRaw = r.cells;
    if (!row || !Array.isArray(cellsRaw)) continue;

    const cells: HeatmapCell[] = [];
    for (const c of cellsRaw) {
      if (!isObj(c)) continue;
      const col = getStr(c, "col");
      const value = c.value;
      if (!col || typeof value !== "number" || !Number.isFinite(value)) continue;

      const top_label = getStr(c, "top_label");
      const top_vertical_id = getStr(c, "top_vertical_id");

      cells.push({
        col,
        value,
        top_label: top_label ?? undefined,
        top_vertical_id: top_vertical_id ?? null,
      });
    }

    if (cells.length) rows.push({ row, cells });
  }

  return rows.length ? { cols, rows } : MOCK_HEATMAP;
}

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

  // Never block UI: always render cockpit.
  const hasApiError = overviewQ.isError || topQ.isError;

  const errMsg = useMemo(() => {
    if (!hasApiError) return null;
    const a = overviewQ.isError ? getErrorMessage(overviewQ.error) : "";
    const b = topQ.isError ? getErrorMessage(topQ.error) : "";
    const joined = [a, b].filter(Boolean).join(" · ");
    return clampText(joined || "Unknown API error");
  }, [hasApiError, overviewQ.error, overviewQ.isError, topQ.error, topQ.isError]);

  const overview = overviewQ.data ?? null;

  const kpis = useMemo(() => normalizeKpis(overview), [overview]);

  const breakouts = useMemo(() => {
    const fromOverview = normalizeBreakoutsFromOverview(overview);
    if (fromOverview && fromOverview.length) return fromOverview;

    const fromTop = normalizeBreakoutsFromTopPains(topQ.data as unknown);
    if (fromTop && fromTop.length) return fromTop;

    return MOCK_BREAKOUTS;
  }, [overview, topQ.data]);

  const heatmap = useMemo(() => normalizeHeatmap(overview), [overview]);

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

      {errMsg ? (
        <div className="sense-panel rounded-2xl border bg-card/40 p-3">
          <div className="text-xs font-semibold">API error</div>
          <div className="mt-1 font-mono text-[11px] text-muted-foreground">{errMsg}</div>
        </div>
      ) : null}

      <MarketPulse kpis={kpis} windowLabel="Window: last 7 days" />

      <TopBreakoutsTable items={breakouts} />

      <Heatmap heatmap={heatmap} />
    </div>
  );
}