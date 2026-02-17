"use client";

import Link from "next/link";
import type { TopPain } from "@/lib/api/schemas";

export function TopOpportunities({ items }: { items: TopPain[] }) {
  const top = items.slice(0, 10);

  return (
    <div className="rounded-md border">
      <div className="border-b px-4 py-3">
        <div className="text-sm font-medium">Top opportunities</div>
        <div className="text-xs text-muted-foreground">Top 10 from /insights/top_pains</div>
      </div>

      <div className="divide-y">
        {top.map((it) => (
          <Link
            key={it.cluster_id}
            href={`/clusters/${encodeURIComponent(it.cluster_id)}`}
            className="block px-4 py-3 hover:bg-muted/40"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="truncate text-sm font-medium">
                  {it.cluster_summary ?? "—"}
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  id: {it.cluster_id} • persona: {it.dominant_persona}
                </div>
              </div>

              <div className="text-right text-xs tabular-nums text-muted-foreground">
                <div>ex: {it.exploitability_score}</div>
                <div>sev: {it.severity_score}</div>
                <div>brk: {it.breakout_score}</div>
                <div>conf: {it.confidence_score}</div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
