"use client";

import { useMemo } from "react";
import { useClusterDetail, useOpsQueues, useOpsRuns, useTopPains } from "@/lib/api/queries";

type QueueItem = { depth?: number | null } & Record<string, unknown>;
type RunItem = { created_at?: string; started_at?: string } & Record<string, unknown>;

function ts(x: unknown): number {
  if (typeof x !== "string") return 0;
  const t = Date.parse(x);
  return Number.isFinite(t) ? t : 0;
}

export default function AnalyticsPage() {
  const topQ = useTopPains({ limit: 50, offset: 0 });
  const queuesQ = useOpsQueues();
  const runsQ = useOpsRuns();

  const top = topQ.data ?? [];
  const firstId = top[0]?.cluster_id ?? "";

  // backward compat: useClusterDetail(id, enabled)
  const detailQ = useClusterDetail(firstId, Boolean(firstId));

  const queues: QueueItem[] = (queuesQ.data?.items ?? []) as QueueItem[];
  const runs: RunItem[] = (runsQ.data?.items ?? []) as RunItem[];

  const latestRun = useMemo(() => {
    return runs
      .slice()
      .sort((a: RunItem, b: RunItem) => ts(b.started_at ?? b.created_at) - ts(a.started_at ?? a.created_at))[0];
  }, [runs]);

  const queueTotalDepth = useMemo(() => {
    return queues.reduce((acc: number, q: QueueItem) => acc + (typeof q.depth === "number" ? q.depth : 0), 0);
  }, [queues]);

  // ---- render (keep your existing UI below if you want; this file only fixes typings) ----
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border bg-card/40 p-4">
        <div className="text-sm font-semibold">Analytics</div>
        <div className="mt-2 text-xs text-muted-foreground font-mono">
          queues={queues.length} depth={queueTotalDepth} · runs={runs.length} · latestRun={latestRun ? "yes" : "no"}
        </div>
      </div>

      <div className="rounded-2xl border bg-card/40 p-4">
        <div className="text-sm font-semibold">Detail Probe</div>
        <div className="mt-2 text-xs text-muted-foreground font-mono">
          cluster_id={firstId || "—"} · detailLoaded={detailQ.data ? "yes" : "no"}
        </div>
      </div>
    </div>
  );
}