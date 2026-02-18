import { getOverview } from "@/lib/api/queries";
import { ErrorBlock } from "@/components/ui/ErrorBlock";
import { OverviewHeader } from "@/components/overview-v2/OverviewHeader";
import { MarketPulse } from "@/components/overview-v2/MarketPulse";
import { TopBreakoutsTable } from "@/components/overview-v2/TopBreakoutsTable";
import { Heatmap, type HeatmapData } from "@/components/overview-v2/Heatmap";

function formatUpdatedLabel(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "Updated recently";
  return `Updated ${d.toLocaleString()}`;
}

function formatKpiValue(n: number): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(n);
}

export default async function OverviewPage() {
  try {
    const api = await getOverview();

    // --- KPI view-model: UI expects strings for value/deltas ---
    const kpis = api.kpis.map((k) => ({
      key: k.key,
      label: k.label,
      value: formatKpiValue(k.value),
      delta_7d: k.delta_7d ?? null,
      sparkline: k.sparkline,
    }));

    // --- Breakouts: backend contract is vertical-centric; UI table supports both cluster + vertical ---
    const items = api.breakouts.map((b) => ({
      // keep compatibility with the table (it uses cluster_id as primary key)
      cluster_id: b.vertical_id,
      vertical_id: b.vertical_id,
      vertical_label: b.vertical_label,
      score: b.score,
      momentum_7d: b.momentum_7d,
      confidence: b.confidence,
      tier: b.tier ?? null,
      status: b.status,
    }));

    // --- Heatmap: backend gives flat cells; UI expects grid {cols, rows} ---
    const heatmap: HeatmapData | null = (() => {
      if (!api.heatmap || api.heatmap.length === 0) return null;

      const industries = Array.from(new Set(api.heatmap.map((c) => c.industry))).sort();
      const functions = Array.from(new Set(api.heatmap.map((c) => c.function))).sort();

      const rowMap = new Map<string, { row: string; cells: { col: string; value: number; top_label?: string | null; top_vertical_id?: string | null }[] }>();

      for (const ind of industries) rowMap.set(ind, { row: ind, cells: [] });

      for (const cell of api.heatmap) {
        const r = rowMap.get(cell.industry);
        if (!r) continue;
        r.cells.push({
          col: cell.function,
          value: typeof cell.value === "number" && Number.isFinite(cell.value) ? cell.value : 0,
          top_label: cell.top_vertical_label ?? null,
          top_vertical_id: cell.top_vertical_id ?? null,
        });
      }

      // Ensure every row has all columns (missing = 0)
      const rows = industries.map((ind) => {
        const base = rowMap.get(ind)!;
        const present = new Map(base.cells.map((c) => [c.col, c]));
        const full = functions.map((col) => present.get(col) ?? { col, value: 0 });
        return { row: ind, cells: full };
      });

      return { cols: functions, rows };
    })();

    return (
      <div className="space-y-6">
        <OverviewHeader updatedLabel={formatUpdatedLabel(api.updated_at)} />
        <MarketPulse kpis={kpis} />
        <TopBreakoutsTable items={items} />
        <Heatmap heatmap={heatmap} />
      </div>
    );
  } catch (e) {
    return (
      <ErrorBlock
        title="Overview failed to load"
        description={
          "The backend response did not match the expected contract or the request failed." +
          (e ? ` (${String(e)})` : "")
        }
      />
    );
  }
}