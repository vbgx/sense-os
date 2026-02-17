"use client";

import { cn } from "@/lib/utils";

export type MarketKpi = {
  key: string;
  label: string;
  value: string;
  delta_7d?: number | null;
  badge?: string | null;
  note?: string | null;
};

function fmtDelta(x?: number | null) {
  if (x === null || x === undefined) return "—";
  const sign = x >= 0 ? "+" : "";
  return `${sign}${x.toFixed(0)}%`;
}

type Props = {
  kpis: MarketKpi[];
  windowLabel?: string;
};

export function MarketPulse({ kpis, windowLabel }: Props) {
  return (
    <div className="rounded-2xl border p-4">
      <div className="flex items-baseline justify-between gap-2">
        <div className="text-sm font-medium">Market pulse</div>
        {windowLabel ? <div className="text-xs text-muted-foreground">{windowLabel}</div> : null}
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((k) => {
          const up = (k.delta_7d ?? 0) >= 0;

          return (
            <div key={k.key} className="relative overflow-hidden rounded-2xl border bg-background/20 p-3">
              <div className="flex items-start justify-between gap-2">
                <div className="text-xs text-muted-foreground">{k.label}</div>
                {k.badge ? (
                  <span className="rounded-full border px-2 py-0.5 text-[11px] text-muted-foreground">
                    {k.badge}
                  </span>
                ) : null}
              </div>

              <div className="mt-2 flex items-end justify-between gap-2">
                <div className="text-2xl font-semibold tracking-tight">{k.value}</div>
                <div className={cn("text-xs font-medium", up ? "text-emerald-300" : "text-rose-300")}>
                  {fmtDelta(k.delta_7d)}
                </div>
              </div>

              <div className="mt-2 text-xs text-muted-foreground">
                {k.note ? <span className="truncate opacity-80">{k.note}</span> : <span className="opacity-60">—</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
