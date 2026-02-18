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

type Props = {
  kpis: MarketKpi[];
  windowLabel?: string;
  subtitle?: string;
};

function fmtDelta(x?: number | null) {
  if (x === null || x === undefined) return "—";
  const sign = x > 0 ? "+" : "";
  return `${sign}${x.toFixed(0)}% 7d`;
}

function deltaTone(x?: number | null) {
  if (x === null || x === undefined) return "text-muted-foreground";
  if (x > 0) return "text-emerald-300";
  if (x < 0) return "text-rose-300";
  return "text-muted-foreground";
}

function sparkStroke(x?: number | null) {
  if (x === null || x === undefined) return "rgba(255,255,255,.65)";
  if (x > 0) return "rgba(39,209,127,.85)";
  if (x < 0) return "rgba(255,90,122,.85)";
  return "rgba(255,255,255,.65)";
}

export function MarketPulse({
  kpis,
  windowLabel = "Window: last 7 days",
  subtitle = "Macro KPIs with 7-day deltas",
}: Props) {
  return (
    <section className="rounded-2xl border bg-card/40 sense-panel">
      <header className="flex items-baseline justify-between gap-3 border-b px-4 py-3">
        <div className="flex flex-col gap-0.5">
          <div className="text-[13px] font-semibold tracking-tight">Market Pulse</div>
          <div className="text-xs text-muted-foreground">{subtitle}</div>
        </div>
        <div className="font-mono text-xs text-muted-foreground">{windowLabel}</div>
      </header>

      <div className="px-4 py-4">
        {kpis.length === 0 ? (
          <div className="rounded-2xl border bg-background/20 p-3">
            <div className="text-xs text-muted-foreground">No market KPIs available.</div>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {kpis.slice(0, 5).map((k) => (
              <article
                key={k.key}
                className={cn(
                  "relative overflow-hidden rounded-2xl border bg-background/20 p-3",
                  "before:absolute before:inset-0 before:bg-[radial-gradient(320px_140px_at_0%_0%,rgba(255,255,255,.06),transparent_65%)] before:content-['']",
                )}
              >
                <div className="relative flex items-start justify-between gap-2">
                  <div className="text-xs text-muted-foreground">{k.label}</div>
                  {k.badge ? (
                    <span className="inline-flex items-center rounded-full border bg-background/10 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                      {k.badge}
                    </span>
                  ) : null}
                </div>

                <div className="relative mt-1.5 text-[22px] font-semibold tracking-tight tabular-nums">
                  {k.value}
                </div>

                <div className="relative mt-2 flex items-center justify-between gap-2 font-mono text-[11px] text-muted-foreground">
                  <span className={cn("tabular-nums", deltaTone(k.delta_7d))}>{fmtDelta(k.delta_7d)}</span>

                  {/* Sparkline (visual only) */}
                  <svg className="h-[18px] w-[64px] opacity-90" viewBox="0 0 64 18" fill="none">
                    <path
                      d="M1 14 L10 12 L18 13 L26 9 L34 10 L42 7 L50 6 L63 4"
                      stroke={sparkStroke(k.delta_7d)}
                      strokeWidth="2"
                    />
                  </svg>
                </div>

                {k.note ? (
                  <div className="relative mt-2 text-xs text-muted-foreground">
                    <span className="line-clamp-1 opacity-75">{k.note}</span>
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
