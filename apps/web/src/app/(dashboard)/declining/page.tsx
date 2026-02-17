"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useDeclining } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";
import type { TopPain } from "@/lib/api/schemas";

function satHint(it: TopPain): string {
  const sat = it.saturation_score ?? 0;
  const conf = it.confidence_score ?? 0;

  if (sat >= 80 && conf >= 70) return "Saturated (high confidence)";
  if (sat >= 80) return "Highly saturated";
  if (sat >= 60) return "Saturating";
  return "Declining / risk";
}

export default function Page() {
  const q = useDeclining({ limit: 200, offset: 0 });

  const items = useMemo(() => {
    const data = q.data ?? [];
    // sort by saturation desc (fallback 0 if not exposed)
    return data.slice().sort((a, b) => (b.saturation_score ?? 0) - (a.saturation_score ?? 0));
  }, [q.data]);

  if (q.isLoading) return <Skeleton className="h-[720px] w-full" />;

  if (q.isError) {
    const msg = q.error instanceof Error ? q.error.message : "Unknown error";
    return (
      <div className="rounded-md border p-3">
        <div className="text-sm font-medium">API error</div>
        <div className="mt-1 text-xs text-muted-foreground">{msg}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <div className="text-xl font-semibold">Declining</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Saturation / decline view • risk hints only • no execution features
        </div>
      </div>

      <div className="rounded-md border p-3 text-sm">
        <div className="font-medium">Risk hints</div>
        <div className="mt-1 text-xs text-muted-foreground">
          Based on saturation_score (if exposed) + confidence_score. Missing saturation falls back to 0.
        </div>
      </div>

      <div className="rounded-md border overflow-hidden">
        <div className="grid grid-cols-12 gap-2 border-b bg-background px-4 py-2 text-xs font-medium text-muted-foreground">
          <div className="col-span-5">Cluster</div>
          <div className="col-span-2">Exploit</div>
          <div className="col-span-2">Breakout</div>
          <div className="col-span-1">Sat</div>
          <div className="col-span-2">Hint</div>
        </div>

        <div className="divide-y">
          {items.map((it: TopPain) => (
            <div key={it.cluster_id} className="grid grid-cols-12 gap-2 px-4 py-3">
              <div className="col-span-5 min-w-0">
                <div className="truncate text-sm font-medium">{it.cluster_summary ?? "—"}</div>
                <div className="mt-1 text-xs text-muted-foreground">
                  id: {it.cluster_id} • persona: {it.dominant_persona || "—"}
                </div>
                <div className="mt-2">
                  <Link
                    className="text-xs underline underline-offset-2"
                    href={`/clusters/${encodeURIComponent(it.cluster_id)}`}
                  >
                    Open deep dive
                  </Link>
                </div>
              </div>

              <div className="col-span-2 text-sm tabular-nums">
                {it.exploitability_score} <span className="text-xs text-muted-foreground">({it.exploitability_tier})</span>
              </div>

              <div className="col-span-2 text-sm tabular-nums">{it.breakout_score}</div>

              <div className="col-span-1 text-sm tabular-nums">{it.saturation_score ?? "—"}</div>

              <div className="col-span-2 text-xs text-muted-foreground">{satHint(it)}</div>
            </div>
          ))}

          {items.length === 0 && (
            <div className="px-4 py-6 text-sm text-muted-foreground">No declining data.</div>
          )}
        </div>
      </div>
    </div>
  );
}
