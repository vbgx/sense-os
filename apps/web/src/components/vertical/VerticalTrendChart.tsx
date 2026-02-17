"use client";

import Link from "next/link";
import type { TrendItem, TrendSparkPoint } from "@/lib/api/schemas";

function MiniSparkline({ values }: { values: number[] }) {
  if (values.length < 2) return <div className="text-xs text-muted-foreground">No sparkline</div>;

  const w = 240;
  const h = 36;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;

  const pts = values.map((v, i) => {
    const x = (i / (values.length - 1)) * w;
    const y = h - ((v - min) / span) * h;
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  });

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="block">
      <polyline fill="none" stroke="currentColor" strokeWidth="2" points={pts.join(" ")} />
    </svg>
  );
}

function pickNumber(p: TrendSparkPoint): number | null {
  if (typeof p.value === "number") return p.value;
  if (typeof p.volume === "number") return p.volume;
  if (typeof p.velocity === "number") return p.velocity;
  return null;
}

function extractSeries(it: TrendItem): number[] {
  const sp = it.sparkline ?? [];
  const out: number[] = [];
  for (const p of sp) {
    const v = pickNumber(p);
    if (v !== null) out.push(v);
  }
  return out;
}

export function VerticalTrendChart({ items }: { items: TrendItem[] }) {
  return (
    <div className="rounded-md border">
      <div className="border-b px-4 py-3">
        <div className="text-sm font-medium">Trend (top clusters)</div>
        <div className="text-xs text-muted-foreground">
          Source: /trending • sparklines per cluster (vertical-aggregate trend not exposed yet)
        </div>
      </div>

      <div className="divide-y">
        {items.slice(0, 10).map((it) => {
          const series = extractSeries(it);
          return (
            <div key={it.cluster_id} className="px-4 py-3">
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">{it.cluster_summary ?? "—"}</div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    id: {it.cluster_id}
                    {typeof it.exploitability_score === "number" ? ` • ex: ${it.exploitability_score}` : ""}
                    {typeof it.breakout_score === "number" ? ` • brk: ${it.breakout_score}` : ""}
                  </div>
                </div>
                <Link
                  className="text-xs underline underline-offset-2"
                  href={`/clusters/${encodeURIComponent(it.cluster_id)}`}
                >
                  Deep dive
                </Link>
              </div>

              <div className="mt-2 text-muted-foreground">
                <MiniSparkline values={series} />
              </div>
            </div>
          );
        })}

        {items.length === 0 && (
          <div className="px-4 py-6 text-sm text-muted-foreground">No trending data.</div>
        )}
      </div>
    </div>
  );
}
