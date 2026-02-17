"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type Props = {
  updatedLabel: string;
  isRefreshing?: boolean;
  onRefresh?: () => void;

  title?: string;
  subtitle?: string;
};

export function OverviewHeader({
  updatedLabel,
  isRefreshing,
  onRefresh,
  title = "Market State Today",
  subtitle = "Macro radar of what’s happening right now: pulse, breakouts, and opportunity density by industry × function. Click a breakout to deep dive, or drill into a heatmap cell to explore its top verticals.",
}: Props) {
  return (
    <section className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div className="max-w-[860px]">
        <h1 className="text-[22px] font-semibold tracking-tight">{title}</h1>
        <p className="mt-1 text-[13px] leading-relaxed text-muted-foreground">{subtitle}</p>
      </div>

      <div className="flex items-center justify-between gap-3 rounded-2xl border bg-card/40 px-3 py-2 sense-panel">
        <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground">
          <span
            className={cn(
              "h-2 w-2 rounded-full",
              "bg-emerald-400 sense-led shadow-[0_0_0_3px_rgba(16,185,129,0.18)]",
            )}
          />
          <span>Live</span>
          <span className="opacity-60">·</span>
          <span className="opacity-80">{updatedLabel}</span>
        </div>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onRefresh}
          disabled={!onRefresh || !!isRefreshing}
          className="font-mono text-xs"
        >
          {isRefreshing ? "Refreshing…" : "Refresh"}
        </Button>
      </div>
    </section>
  );
}
