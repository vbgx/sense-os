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
  const sign = x > 0 ? "+" : "";
  return `${sign}${x.toFixed(0)}%`;
}

function deltaTone(x?: number | null) {
  if (x === null || x === undefined) return "text-muted-foreground";
  if (x > 0) return "text-emerald-300";
  if (x < 0) return "text-rose-300";
  return "text-muted-foreground";
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
        {windowLabel ? <div className="text-xs text-muted-foreground">{windowLabel}</div> : null}
      </header>

      {kpis.length === 0 ? (
        <div className="mt-3 rounded-2xl border bg-background/20 p-3">
          <div className="text-xs text-muted-foreground">No KPIs available.</div>
        </div>
      ) : (
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {kpis.map((k) => (
            <article key={k.key} className="overflow-hidden rounded-2xl border bg-background/20 p-3">
              <div className="flex items-start justify-between gap-2">
                <div className="text-xs text-muted-foreground">{k.label}</div>
                {k.badge ? (
                  <span className="rounded-full border px-2 py-0.5 text-[11px] text-muted-foreground">
                    {k.badge}
                  </span>
                ) : null}
              </div>

              <div className="mt-2 flex items-end justify-between gap-2">
                <div className="text-2xl font-semibold tracking-tight tabular-nums">{k.value}</div>
                <div className={cn("text-xs font-medium tabular-nums", deltaTone(k.delta_7d))}>
                  {fmtDelta(k.delta_7d)}
                </div>
              </div>

              <div className="mt-2 text-xs text-muted-foreground">
                {k.note ? <span className="line-clamp-1 opacity-80">{k.note}</span> : <span className="opacity-60">—</span>}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

/**
 * Optional skeleton (use in Overview loading state if you want 0 layout shift)
 * Keep it colocated to avoid design drift.
 */
export function MarketPulseSkeleton({ windowLabel }: { windowLabel?: string }) {
  return (
    <section className="rounded-2xl border bg-card/40 p-4">
      <header className="flex items-baseline justify-between gap-2">
        <div className="h-4 w-28 animate-pulse rounded-md bg-muted/40" />
        {windowLabel ? <div className="text-xs text-muted-foreground">{windowLabel}</div> : null}
      </header>

      <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="overflow-hidden rounded-2xl border bg-background/20 p-3">
            <div className="flex items-start justify-between gap-2">
              <div className="h-3 w-24 animate-pulse rounded-md bg-muted/40" />
              <div className="h-5 w-12 animate-pulse rounded-full bg-muted/30" />
            </div>
            <div className="mt-3 flex items-end justify-between gap-2">
              <div className="h-7 w-24 animate-pulse rounded-md bg-muted/40" />
              <div className="h-4 w-12 animate-pulse rounded-md bg-muted/30" />
            </div>
            <div className="mt-3 h-3 w-40 animate-pulse rounded-md bg-muted/30" />
          </div>
        ))}
      </div>
    </section>
  );
}
