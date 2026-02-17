//mock//
"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useClusterDetail } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";
import { ClusterTimelineChart } from "@/components/charts/ClusterTimelineChart";
import { ScoreBreakdownChart } from "@/components/charts/ScoreBreakdownChart";

export default function Page() {
  const params = useParams<{ id: string }>();
  const clusterId = params.id;

  const q = useClusterDetail(clusterId);

  if (q.isLoading) return <Skeleton className="h-[420px] w-full" />;

  if (q.isError || !q.data) {
    return (
      <div className="rounded-md border p-3">
        <div className="text-sm font-medium">Failed to load cluster</div>
        <div className="mt-1 text-xs text-muted-foreground">
          {q.error instanceof Error ? q.error.message : "Unknown error"}
        </div>
      </div>
    );
  }

  const c = q.data;

  const breakdown = [
    { name: "Exploitability", value: c.exploitability_score },
    { name: "Severity", value: c.severity_score },
    { name: "Recurrence", value: c.recurrence_score },
    { name: "Monetizability", value: c.monetizability_score },
    { name: "Breakout", value: c.breakout_score },
    { name: "Competition", value: c.competitive_heat_score },
    { name: "Contradiction", value: c.contradiction_score },
    { name: "Confidence", value: c.confidence_score },
  ];

  const topPhrases = c.key_phrases.slice(0, 12);
  const topSignals = c.representative_signals.slice(0, 6);

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold" data-testid="cluster-title">
              {c.cluster_id}
            </h1>
            <div className="text-sm text-muted-foreground">
              window: {c.opportunity_window_status} • tier: {c.exploitability_tier} • confidence: {c.confidence_score}
            </div>
          </div>

          <Link
            href="/opportunities"
            className="rounded-md border px-3 py-2 text-sm hover:bg-muted"
          >
            Back to board
          </Link>
        </div>

        <div className="rounded-md border p-4">
          <div className="text-xs font-medium text-muted-foreground">Summary</div>
          <div className="mt-2 text-sm">{c.cluster_summary ?? "—"}</div>
        </div>
      </div>

      {/* Identity */}
      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-md border p-4 space-y-2">
          <div className="text-sm font-medium">Identity</div>
          <div className="text-sm">
            <div>Exploitability: {c.exploitability_score} ({c.exploitability_tier})</div>
            <div>Exploitability v2: {c.exploitability_score_v2} ({c.exploitability_tier_v2})</div>
            <div>Exploitability v2 version: {c.exploitability_version_v2}</div>
            <div>Confidence: {c.confidence_score}</div>
          </div>
        </div>

        <div className="rounded-md border p-4 space-y-2">
          <div className="text-sm font-medium">Structure</div>
          <div className="text-sm">
            <div>Severity: {c.severity_score}</div>
            <div>Recurrence: {c.recurrence_score}</div>
            <div>Monetizability: {c.monetizability_score}</div>
          </div>
        </div>
      </section>

      {/* Timing */}
      <section className="rounded-md border p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium">Timing</div>
          <div className="text-xs text-muted-foreground">
            breakout: {c.breakout_score} • window: {c.opportunity_window_status}
          </div>
        </div>
        <ClusterTimelineChart data={c.timeline} />
      </section>

      {/* Structure details */}
      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-md border p-4">
          <div className="text-sm font-medium">Key phrases</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {topPhrases.length ? (
              topPhrases.map((p) => (
                <span key={p} className="rounded-md border px-2 py-1 text-xs">
                  {p}
                </span>
              ))
            ) : (
              <span className="text-xs text-muted-foreground">—</span>
            )}
          </div>
        </div>

        <div className="rounded-md border p-4">
          <div className="text-sm font-medium">Representative signals</div>
          <div className="mt-3 space-y-2">
            {topSignals.length ? (
              topSignals.map((s) => (
                <div key={s.id} className="rounded-md border p-2 text-sm">
                  <div className="text-xs text-muted-foreground">signal_id: {s.id}</div>
                  <div className="mt-1">{s.text}</div>
                </div>
              ))
            ) : (
              <span className="text-xs text-muted-foreground">—</span>
            )}
          </div>
        </div>
      </section>

      {/* Competition */}
      <section className="rounded-md border p-4 space-y-2">
        <div className="text-sm font-medium">Competition</div>
        <div className="text-sm">
          <div>Competitive heat: {c.competitive_heat_score}</div>
        </div>
      </section>

      {/* Breakdown */}
      <section className="rounded-md border p-4 space-y-3">
        <div className="text-sm font-medium">Breakdown</div>
        <div className="text-xs text-muted-foreground">
          Risk flags proxies: contradiction={c.contradiction_score} • window={c.opportunity_window_status}
        </div>
        <ScoreBreakdownChart data={breakdown} />
      </section>
    </div>
  );
}
