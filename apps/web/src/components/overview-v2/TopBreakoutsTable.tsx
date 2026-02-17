"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

export type BreakoutRow = {
  cluster_id: string;
  cluster_summary?: string | null;
  score?: number | null;
  breakout_score?: number | null;
  confidence_score?: number | null;
  tier?: string | null;
  status?: string | null;
};

type Props = {
  items: BreakoutRow[];
};

function n(x?: number | null) {
  if (x === null || x === undefined) return "—";
  return String(x);
}

export function TopBreakoutsTable({ items }: Props) {
  return (
    <div className="rounded-2xl border">
      <div className="flex items-baseline justify-between gap-2 p-4">
        <div className="text-sm font-medium">Top breakouts</div>
        <div className="text-xs text-muted-foreground">{items.length} items</div>
      </div>

      <div className="divide-y">
        {items.length === 0 ? (
          <div className="p-4 text-sm text-muted-foreground">No breakouts in this window.</div>
        ) : (
          items.map((it) => (
            <div key={it.cluster_id} className="flex items-center justify-between gap-3 p-4">
              <div className="min-w-0">
                <div className="truncate text-sm font-medium">{it.cluster_summary ?? it.cluster_id}</div>
                <div className="mt-1 flex flex-wrap gap-2 text-xs text-muted-foreground">
                  <span>Exploitability: {n(it.score)}</span>
                  <span>Breakout: {n(it.breakout_score)}</span>
                  <span>Confidence: {n(it.confidence_score)}</span>
                  {it.tier ? <span>Tier: {it.tier}</span> : null}
                  {it.status ? <span>Status: {it.status}</span> : null}
                </div>
              </div>

              <Button asChild variant="outline" size="sm">
                <Link href={`/clusters/${encodeURIComponent(it.cluster_id)}`}>Open</Link>
              </Button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
