"use client";

import { useMemo } from "react";
import type { TopPain } from "@/lib/api/schemas";

export function VerticalTierDistribution({ items }: { items: TopPain[] }) {
  const rows = useMemo(() => {
    const m = new Map<string, number>();
    for (const it of items) {
      const k = it.exploitability_tier || "UNKNOWN";
      m.set(k, (m.get(k) ?? 0) + 1);
    }
    return Array.from(m.entries())
      .map(([tier, count]) => ({ tier, count }))
      .sort((a, b) => b.count - a.count);
  }, [items]);

  return (
    <div className="rounded-md border">
      <div className="border-b px-4 py-3">
        <div className="text-sm font-medium">Exploitability tier distribution</div>
        <div className="text-xs text-muted-foreground">Computed from /insights/top_pains (filtered by vertical)</div>
      </div>

      <div className="divide-y">
        {rows.map((r) => (
          <div key={r.tier} className="flex items-center justify-between px-4 py-3">
            <div className="text-sm">{r.tier}</div>
            <div className="text-sm tabular-nums">{r.count}</div>
          </div>
        ))}
        {rows.length === 0 && (
          <div className="px-4 py-6 text-sm text-muted-foreground">No tier data.</div>
        )}
      </div>
    </div>
  );
}
