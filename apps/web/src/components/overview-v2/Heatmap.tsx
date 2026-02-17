"use client";

import { useMemo } from "react";
import { cn } from "@/lib/utils";

export type HeatmapCell = {
  col: string;
  value: number;
  top_label?: string | null;
  top_vertical_id?: string | null;
};

export type HeatmapRow = {
  row: string;
  cells: HeatmapCell[];
};

export type HeatmapData = {
  cols: string[];
  rows: HeatmapRow[];
};

type Props = {
  heatmap?: HeatmapData | null;
  onCellClick?: (args: { row: string; col: string; cell: HeatmapCell }) => void;
  subtitle?: string;
};

function clamp01(x: number) {
  if (!Number.isFinite(x)) return 0;
  return Math.max(0, Math.min(1, x));
}

/**
 * Real gradient like mock (inset tint).
 */
function densityTint(v01: number): string {
  const v = clamp01(v01);

  const stops = [
    { t: 0.0, r: 255, g: 255, b: 255, a: 0.01 },
    { t: 0.25, r: 39, g: 209, b: 127, a: 0.06 },
    { t: 0.5, r: 39, g: 209, b: 127, a: 0.11 },
    { t: 0.75, r: 255, g: 191, b: 60, a: 0.10 },
    { t: 1.0, r: 255, g: 107, b: 61, a: 0.14 },
  ] as const;

  const i = stops.findIndex((s, idx) => idx < stops.length - 1 && v >= s.t && v <= stops[idx + 1].t);
  const idx = i === -1 ? stops.length - 2 : i;

  const s0 = stops[idx];
  const s1 = stops[idx + 1];
  const span = s1.t - s0.t || 1;
  const p = (v - s0.t) / span;

  const r = Math.round(s0.r + (s1.r - s0.r) * p);
  const g = Math.round(s0.g + (s1.g - s0.g) * p);
  const b = Math.round(s0.b + (s1.b - s0.b) * p);
  const a = +(s0.a + (s1.a - s0.a) * p).toFixed(3);

  return `inset 0 0 0 999px rgba(${r},${g},${b},${a})`;
}

export function Heatmap({
  heatmap,
  onCellClick,
  subtitle = "Opportunity density (score × momentum). Click to drill down.",
}: Props) {
  const cols = heatmap?.cols ?? [];
  const rows = heatmap?.rows ?? [];

  const colCount = cols.length;

  const gridStyle = useMemo(() => {
    const n = Math.max(1, colCount);
    return {
      gridTemplateColumns: `160px repeat(${n}, minmax(0, 1fr))`,
    } as const;
  }, [colCount]);

  return (
    <section className="sense-panel rounded-2xl border bg-card/40">
      <header className="flex items-baseline justify-between gap-3 border-b px-4 py-3">
        <div className="flex flex-col gap-0.5">
          <div className="text-[13px] font-semibold tracking-tight">Industry × Function Heatmap</div>
          <div className="text-xs text-muted-foreground">{subtitle}</div>
        </div>
        <div className="font-mono text-xs text-muted-foreground">Density: low → high</div>
      </header>

      <div className="px-4 py-4">
        {!heatmap || rows.length === 0 || cols.length === 0 ? (
          <div className="rounded-2xl border bg-background/20 p-3">
            <div className="text-xs text-muted-foreground">No heatmap data.</div>
          </div>
        ) : (
          <div className="grid gap-2" style={gridStyle}>
            <div className="px-2 py-2 font-mono text-[11px] text-muted-foreground/70" />

            {cols.map((c) => (
              <div key={c} className="border-b px-2 py-2 font-mono text-[11px] text-muted-foreground">
                {c}
              </div>
            ))}

            {rows.map((r) => (
              <RowBlock key={r.row} row={r} cols={cols} onCellClick={onCellClick} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

function RowBlock({
  row,
  cols,
  onCellClick,
}: {
  row: HeatmapRow;
  cols: string[];
  onCellClick?: (args: { row: string; col: string; cell: HeatmapCell }) => void;
}) {
  const map = useMemo(() => {
    const m = new Map<string, HeatmapCell>();
    for (const c of row.cells) m.set(c.col, c);
    return m;
  }, [row.cells]);

  return (
    <>
      <div className="flex items-center gap-2 border-r px-2 py-2 text-xs text-muted-foreground">
        <span className="text-[12px] text-muted-foreground">{row.row}</span>
      </div>

      {cols.map((col) => {
        const cell = map.get(col) ?? { col, value: 0 };
        const v = clamp01(cell.value);

        const boxShadow = densityTint(v);

        const label =
          v >= 0.8 ? "Hot pocket" : v >= 0.6 ? "Stable" : v >= 0.4 ? "Exploring" : v >= 0.2 ? "Emerging" : "Low";

        return (
          <button
            key={`${row.row}__${col}`}
            type="button"
            className={cn(
              "min-h-[58px] rounded-2xl border bg-background/20 p-2 text-left",
              "hover:bg-background/30 hover:border-white/20",
            )}
            style={{ boxShadow }}
            onClick={() => onCellClick?.({ row: row.row, col, cell })}
            title={`${row.row} × ${col} · density ${v.toFixed(2)}`}
          >
            <div className="flex items-center justify-between gap-2 font-mono text-[11px] text-muted-foreground/70">
              <span>density</span>
              <span className="tabular-nums">{v.toFixed(2)}</span>
            </div>

            <div className="mt-1 text-sm font-medium">{label}</div>

            <div className="mt-0.5 font-mono text-[11px] text-muted-foreground/70">
              {cell.top_label ? `top: ${cell.top_label}` : "—"}
            </div>
          </button>
        );
      })}
    </>
  );
}
