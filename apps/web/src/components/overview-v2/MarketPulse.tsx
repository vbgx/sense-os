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
    <section className="rounded-2xl border bg-card/40 p-4">
      <header className="flex items-baseline justify-between gap-2">
        <div className="text-sm font-semibold tracking-tight">Market pulse</div>
        {windowLabel ? (
          <div className="text-xs text-muted-foreground">{windowLabel}</div>
        ) : null}
      </header>

      {kpis.length === 0 ? (
        <div className="mt-3 rounded-2xl border bg-background/20 p-3">
          <div className="text-xs text-muted-foreground">No market KPIs available.</div>
        </div>
      ) : (
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {kpis.map((k) => {
            const d = k.delta_7d;
            const up = d === null || d === undefined ? true : d >= 0;

            return (
              <div
                key={k.key}
                className="relative overflow-hidden rounded-2xl border bg-background/20 p-3"
              >
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
                  <div
                    className={cn(
                      "text-xs font-medium tabular-nums",
                      d === null || d === undefined
                        ? "text-muted-foreground"
                        : up
                          ? "text-emerald-300"
                          : "text-rose-300",
                    )}
                    aria-label={d === null || d === undefined ? "No delta available" : `Delta ${fmtDelta(d)}`}
                  >
                    {fmtDelta(d)}
                  </div>
                </div>

                <div className="mt-2 text-xs text-muted-foreground">
                  {k.note ? (
                    <span className="line-clamp-1 opacity-80">{k.note}</span>
                  ) : (
                    <span className="opacity-60">—</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
