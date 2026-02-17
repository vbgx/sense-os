"use client";

import Link from "next/link";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { useClusterDetail } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";
import type { RepresentativeSignal } from "@/lib/api/schemas";

function SignalRow({ s }: { s: RepresentativeSignal }) {
  return (
    <div className="space-y-1 rounded-md border p-2">
      <div className="text-xs text-muted-foreground">signal_id: {s.id}</div>
      <div className="text-sm">{s.text}</div>
    </div>
  );
}

export function ClusterInspectDrawer() {
  const { state, update } = useDashboardQueryState();
  const clusterId = state.inspect;

  const q = useClusterDetail(clusterId ?? "");
  const open = Boolean(clusterId);

  return (
    <Sheet
      open={open}
      onOpenChange={(next) => {
        if (!next) update({ inspect: undefined });
      }}
    >
      <SheetContent
        side="right"
        className="w-[480px] sm:w-[520px]"
        data-testid="cluster-inspect-drawer"
      >
        <SheetHeader>
          <SheetTitle>Inspect</SheetTitle>
        </SheetHeader>

        {clusterId && q.isLoading && (
          <div className="mt-4 space-y-3">
            <Skeleton className="h-6 w-2/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-24 w-full" />
          </div>
        )}

        {clusterId && q.isError && (
          <div className="mt-4 rounded-md border p-3">
            <div className="text-sm font-medium">Failed to load cluster</div>
            <div className="mt-1 text-xs text-muted-foreground">
              {q.error instanceof Error ? q.error.message : "Unknown error"}
            </div>
          </div>
        )}

        {clusterId && q.data && (
          <div className="mt-4 space-y-4">
            <div className="space-y-1">
              <div className="text-lg font-semibold">{q.data.cluster_id}</div>
              <div className="text-xs text-muted-foreground">
                tier: {q.data.exploitability_tier} • window: {q.data.opportunity_window_status}
              </div>
            </div>

            <div className="rounded-md border p-3">
              <div className="text-xs font-medium text-muted-foreground">Summary</div>
              <div className="mt-2 text-sm">{q.data.cluster_summary ?? "—"}</div>
            </div>

            <div className="rounded-md border p-3">
              <div className="text-xs font-medium text-muted-foreground">Key scores</div>
              <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                <div>Exploitability: {q.data.exploitability_score}</div>
                <div>Severity: {q.data.severity_score}</div>
                <div>Recurrence: {q.data.recurrence_score}</div>
                <div>Monetizability: {q.data.monetizability_score}</div>
                <div>Breakout: {q.data.breakout_score}</div>
                <div>Confidence: {q.data.confidence_score}</div>
              </div>
            </div>

            <div className="rounded-md border p-3">
              <div className="text-xs font-medium text-muted-foreground">Key phrases</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {q.data.key_phrases.slice(0, 5).map((p: string) => (
                  <span key={p} className="rounded-md border px-2 py-1 text-xs">
                    {p}
                  </span>
                ))}
                {q.data.key_phrases.length === 0 && (
                  <span className="text-xs text-muted-foreground">—</span>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-medium text-muted-foreground">
                Representative signals
              </div>
              <div className="space-y-2">
                {q.data.representative_signals.slice(0, 3).map((s: RepresentativeSignal) => (
                  <SignalRow key={s.id} s={s} />
                ))}
                {q.data.representative_signals.length === 0 && (
                  <div className="text-xs text-muted-foreground">—</div>
                )}
              </div>
            </div>

            <div className="pt-2">
              <Link
                href={`/clusters/${encodeURIComponent(q.data.cluster_id)}`}
                className="inline-flex items-center justify-center rounded-md border px-3 py-2 text-sm hover:bg-muted"
              >
                Open Deep Dive
              </Link>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
