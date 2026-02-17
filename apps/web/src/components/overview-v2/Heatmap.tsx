"use client";

export type HeatmapCell = {
  col: string;
  value: number;
};

export type HeatmapRow = {
  row: string;
  cells: HeatmapCell[];
};

export type HeatmapData = {
  rows: HeatmapRow[];
  cols: string[];
};

type Props = {
  heatmap?: HeatmapData | null;
};

function clamp01(x: number) {
  if (x < 0) return 0;
  if (x > 1) return 1;
  return x;
}

export function Heatmap({ heatmap }: Props) {
  const cols = heatmap?.cols ?? [];
  const rows = heatmap?.rows ?? [];

  if (cols.length === 0 || rows.length === 0) {
    return (
      <div className="rounded-2xl border p-4">
        <div className="text-sm font-medium">Heatmap</div>
        <div className="mt-2 text-sm text-muted-foreground">No heatmap data yet.</div>
      </div>
    );
  }

  const max = Math.max(
    1,
    ...rows.flatMap((r) => r.cells.map((c) => c.value))
  );

  return (
    <div className="rounded-2xl border">
      <div className="p-4">
        <div className="text-sm font-medium">Heatmap</div>
        <div className="mt-1 text-xs text-muted-foreground">Density by segment (placeholder viz)</div>
      </div>

      <div className="overflow-auto p-4 pt-0">
        <div className="min-w-[640px]">
          <div className="mb-2 grid" style={{ gridTemplateColumns: `160px repeat(${cols.length}, minmax(56px, 1fr))` }}>
            <div />
            {cols.map((c) => (
              <div key={c} className="px-1 text-center text-[11px] text-muted-foreground">
                {c}
              </div>
            ))}
          </div>

          <div className="space-y-2">
            {rows.map((r) => (
              <div
                key={r.row}
                className="grid items-center gap-1"
                style={{ gridTemplateColumns: `160px repeat(${cols.length}, minmax(56px, 1fr))` }}
              >
                <div className="pr-2 text-xs text-muted-foreground">{r.row}</div>

                {cols.map((c) => {
                  const cell = r.cells.find((x) => x.col === c);
                  const v = cell?.value ?? 0;
                  const a = clamp01(v / max);

                  return (
                    <div
                      key={`${r.row}-${c}`}
                      className="h-8 rounded-md border"
                      style={{ opacity: 0.15 + a * 0.85 }}
                      title={`${r.row} / ${c}: ${v}`}
                    />
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
