"use client";

import { useMemo } from "react";
import { Skeleton } from "@/components/ui/Skeleton";
import { useOpsQueues, useOpsRuns, useTopPains, useClusterDetail } from "@/lib/api/queries";
import type { OpsQueueItem, OpsRunItem, TopPain } from "@/lib/api/schemas";

function fmtAge(seconds: number | undefined): string {
  if (seconds === undefined || !Number.isFinite(seconds)) return "—";
  const s = Math.max(0, Math.floor(seconds));
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h}h`;
  const d = Math.floor(h / 24);
  return `${d}d`;
}

function safeRunId(r: OpsRunItem): string {
  return r.run_id || r.id || "—";
}

function safeTime(s?: string): string {
  if (!s) return "—";
  // keep it human, don't parse aggressively (avoid timezone edge-cases)
  return s.replace("T", " ").replace("Z", " UTC");
}

function dist(values: number[], bins: number[] = [0, 20, 40, 60, 80, 100]) {
  const out = bins.slice(0, -1).map((from, i) => {
    const to = bins[i + 1];
    const count = values.filter((v) => v >= from && v < to).length;
    return { label: `${from}-${to}`, count };
  });
  // include 100 exactly into last bin
  const last = out[out.length - 1];
  last.count += values.filter((v) => v === 100).length;
  return out;
}

function DistCard({ title, values }: { title: string; values: number[] }) {
  const rows = useMemo(() => dist(values), [values]);
  return (
    <div className="rounded-md border">
      <div className="border-b px-4 py-3">
        <div className="text-sm font-medium">{title}</div>
        <div className="text-xs text-muted-foreground">Distribution (computed from Top Pains sample)</div>
      </div>
      <div className="divide-y">
        {rows.map((r) => (
          <div key={r.label} className="flex items-center justify-between px-4 py-3">
            <div className="text-xs text-muted-foreground">{r.label}</div>
            <div className="text-sm tabular-nums">{r.count}</div>
          </div>
        ))}
        {values.length === 0 && (
          <div className="px-4 py-6 text-sm text-muted-foreground">No data.</div>
        )}
      </div>
    </div>
  );
}

export default function Page() {
  // 1) Sample of clusters to compute distributions (infra-safe transparency)
  const topQ = useTopPains({ limit: 200, offset: 0 });

  // 2) Grab scoring version from one real cluster detail (product transparency)
  const firstId = (topQ.data?.[0] as TopPain | undefined)?.cluster_id ?? "";
  const detailQ = useClusterDetail(firstId, Boolean(firstId));

  // 3) Ops transparency (queues + runs)
  const queuesQ = useOpsQueues();
  const runsQ = useOpsRuns();

  const loading = topQ.isLoading || queuesQ.isLoading || runsQ.isLoading || (detailQ.isLoading && Boolean(firstId));
  if (loading) return <Skeleton className="h-[760px] w-full" />;

  const anyError = topQ.isError || queuesQ.isError || runsQ.isError || detailQ.isError;
  if (anyError) {
    const msg =
      (topQ.error instanceof Error && topQ.error.message) ||
      (queuesQ.error instanceof Error && queuesQ.error.message) ||
      (runsQ.error instanceof Error && runsQ.error.message) ||
      (detailQ.error instanceof Error && detailQ.error.message) ||
      "Unknown error";
    return (
      <div className="rounded-md border p-3">
        <div className="text-sm font-medium">API error</div>
        <div className="mt-1 text-xs text-muted-foreground">{msg}</div>
      </div>
    );
  }

  const top = topQ.data ?? [];
  const queues = queuesQ.data?.items ?? [];
  const runs = runsQ.data?.items ?? [];

  const exploitability = top.map((t) => t.exploitability_score).filter((n): n is number => Number.isFinite(n));
  const breakout = top.map((t) => t.breakout_score).filter((n): n is number => Number.isFinite(n));
  const saturation = top
    .map((t) => {
      const maybe = (t as Record<string, unknown>)["saturation_score"];
      return typeof maybe === "number" ? maybe : undefined;
    })
    .filter((n): n is number => typeof n === "number" && Number.isFinite(n));
  const confidence = top.map((t) => t.confidence_score).filter((n): n is number => Number.isFinite(n));

  const latestRun = runs.slice().sort((a, b) => {
    const ta = Date.parse(a.started_at ?? "") || 0;
    const tb = Date.parse(b.started_at ?? "") || 0;
    return tb - ta;
  })[0];

  const scoringVersion = detailQ.data?.exploitability_version_v2 ?? "—";
  const scoringTier = detailQ.data?.exploitability_tier_v2 ?? "—";

  const queueTotalDepth = queues.reduce((acc: number, q) => acc + (q.depth ?? 0), 0);

  return (
    <div className="space-y-6">
      <div>
        <div className="text-xl font-semibold">Analytics</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Transparency view • product-facing metrics only • no infra details
        </div>
      </div>

      {/* KPI row */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-md border p-4">
          <div className="text-xs text-muted-foreground">Sample size</div>
          <div className="mt-1 text-2xl font-semibold tabular-nums">{top.length}</div>
          <div className="mt-1 text-xs text-muted-foreground">Top pains fetched (limit=200)</div>
        </div>

        <div className="rounded-md border p-4">
          <div className="text-xs text-muted-foreground">Scoring version</div>
          <div className="mt-1 text-2xl font-semibold">{scoringVersion}</div>
          <div className="mt-1 text-xs text-muted-foreground">Exploitability tier: {scoringTier}</div>
        </div>

        <div className="rounded-md border p-4">
          <div className="text-xs text-muted-foreground">Queue backlog</div>
          <div className="mt-1 text-2xl font-semibold tabular-nums">{queueTotalDepth}</div>
          <div className="mt-1 text-xs text-muted-foreground">Sum of exposed queue depths</div>
        </div>

        <div className="rounded-md border p-4">
          <div className="text-xs text-muted-foreground">Last run</div>
          <div className="mt-1 text-sm font-medium">{latestRun ? safeRunId(latestRun) : "—"}</div>
          <div className="mt-1 text-xs text-muted-foreground">
            started: {latestRun ? safeTime(latestRun.started_at) : "—"}
          </div>
        </div>
      </div>

      {/* Data freshness + runs */}
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-md border">
          <div className="border-b px-4 py-3">
            <div className="text-sm font-medium">Data freshness</div>
            <div className="text-xs text-muted-foreground">Derived from ops runs (not infra)</div>
          </div>
          <div className="px-4 py-3 text-sm">
            <div>Latest run: {latestRun ? safeRunId(latestRun) : "—"}</div>
            <div className="text-xs text-muted-foreground mt-1">
              started_at: {latestRun ? safeTime(latestRun.started_at) : "—"} • finished_at:{" "}
              {latestRun ? safeTime(latestRun.finished_at) : "—"}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Note: This indicates pipeline recency. Cluster-level updated_at is not exposed in TopPains payload.
            </div>
          </div>
        </div>

        <div className="rounded-md border">
          <div className="border-b px-4 py-3">
            <div className="text-sm font-medium">Runs (latest)</div>
            <div className="text-xs text-muted-foreground">Status-oriented, infra-free</div>
          </div>
          <div className="divide-y">
            {runs.slice(0, 8).map((r, idx: number) => (
              <div key={`${safeRunId(r)}-${idx}`} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium">{safeRunId(r)}</div>
                  <div className="text-xs text-muted-foreground">{r.status ?? "—"}</div>
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  started: {safeTime(r.started_at)} • finished: {safeTime(r.finished_at)}
                </div>
              </div>
            ))}
            {runs.length === 0 && (
              <div className="px-4 py-6 text-sm text-muted-foreground">No runs exposed.</div>
            )}
          </div>
        </div>
      </div>

      {/* Queues */}
      <div className="rounded-md border">
        <div className="border-b px-4 py-3">
          <div className="text-sm font-medium">Queue health</div>
          <div className="text-xs text-muted-foreground">Backlog & lag only (no infra identifiers)</div>
        </div>

        <div className="grid grid-cols-12 gap-2 border-b bg-background px-4 py-2 text-xs font-medium text-muted-foreground">
          <div className="col-span-6">Queue</div>
          <div className="col-span-2">Depth</div>
          <div className="col-span-2">Lag</div>
          <div className="col-span-2">Oldest</div>
        </div>

        <div className="divide-y">
          {queues.map((q: OpsQueueItem, idx: number) => (
            <div key={`${q.name ?? "queue"}-${idx}`} className="grid grid-cols-12 gap-2 px-4 py-3">
              <div className="col-span-6 text-sm font-medium">{q.name ?? "—"}</div>
              <div className="col-span-2 text-sm tabular-nums">{q.depth ?? 0}</div>
              <div className="col-span-2 text-sm tabular-nums">{fmtAge(q.lag_seconds)}</div>
              <div className="col-span-2 text-sm tabular-nums">{fmtAge(q.oldest_age_seconds)}</div>
            </div>
          ))}
          {queues.length === 0 && (
            <div className="px-4 py-6 text-sm text-muted-foreground">No queues exposed.</div>
          )}
        </div>
      </div>

      {/* Metric distributions */}
      <div className="grid gap-4 lg:grid-cols-2">
        <DistCard title="Exploitability score" values={exploitability} />
        <DistCard title="Breakout score" values={breakout} />
        <DistCard title="Confidence score" values={confidence} />
        <DistCard title="Saturation score (if exposed)" values={saturation} />
      </div>
    </div>
  );
}
