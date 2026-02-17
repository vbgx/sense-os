"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { useDeclining } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/button";
import type { TopPain } from "@/lib/api/schemas";

function parseNum(v: string | null, fallback: number) {
  if (!v) return fallback;
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}

function Badge({ children }: { children: string }) {
  return <span className="rounded-md border px-2 py-1 text-xs">{children}</span>;
}

function riskHint(it: TopPain) {
  // Operator hints only (no pretending we have more signals than the contract exposes).
  const sat = it.saturation_score;
  const conf = it.confidence_score;

  if (sat >= 80 && conf >= 70) return "Saturated (high confidence)";
  if (sat >= 80) return "Highly saturated";
  if (sat >= 60) return "Saturating";
  return "Declining risk";
}

export default function Page() {
  const { state, update, reset } = useDashboardQueryState();

  const sp = typeof window !== "undefined" ? new URLSearchParams(window.location.search) : null;
  const minSaturation = parseNum(sp?.get("min_saturation") ?? null, 0);
  const minConfidence = parseNum(sp?.get("min_confidence") ?? null, 0);
  const persona = sp?.get("persona") ?? "";

  const q = useDeclining({
    limit: 200,
    offset: 0,
    vertical_id: state.vertical_id,
  });

  const rows = useMemo(() => {
    const base = (q.data ?? []).slice();

    const filtered = base.filter((it) => {
      if (minSaturation && it.saturation_score < minSaturation) return false;
      if (minConfidence && it.confidence_score < minConfidence) return false;
      if (persona && it.dominant_persona !== persona) return false;
      return true;
    });

    filtered.sort((a, b) => b.saturation_score - a.saturation_score);
    return filtered;
  }, [q.data, minSaturation, minConfidence, persona]);

  const personas = useMemo(() => {
    const set = new Set<string>();
    for (const it of q.data ?? []) set.add(it.dominant_persona);
    return Array.from(set).sort();
  }, [q.data]);

  if (q.isLoading) return <Skeleton className="h-[640px] w-full" />;

  if (q.isError) {
    return (
      <div className="rounded-md border p-3">
        <div className="text-sm font-medium">API error</div>
        <div className="mt-1 text-xs text-muted-foreground">
          {q.error instanceof Error ? q.error.message : "Unknown error"}
        </div>
      </div>
    );
  }

  const setParam = (key: string, value: string | number | undefined) => {
    const params = new URLSearchParams(window.location.search);
    if (value === undefined || value === "" || value === 0) params.delete(key);
    else params.set(key, String(value));
    const url = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState(null, "", url);
    update({ offset: state.offset }); // trigger rerender via state hook side effect
  };

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Declining</h1>
          <p className="text-sm text-muted-foreground">
            SATURATING window • sorted by saturation desc • {rows.length} clusters
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={reset}>
          Reset dashboard filters
        </Button>
      </div>

      {/* Quick filters */}
      <div className="flex flex-wrap items-center gap-2 rounded-md border p-3">
        <div className="text-xs text-muted-foreground">Quick filters</div>

        <Button
          size="sm"
          variant="outline"
          onClick={() => setParam("min_saturation", 70)}
        >
          Saturation ≥ 70
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setParam("min_saturation", 85)}
        >
          Saturation ≥ 85
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setParam("min_confidence", 70)}
        >
          Confidence ≥ 70
        </Button>

        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Persona</span>
          <select
            className="h-9 rounded-md border bg-background px-2 text-sm"
            value={persona}
            onChange={(e) => setParam("persona", e.target.value)}
          >
            <option value="">All</option>
            {personas.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>

          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setParam("min_saturation", undefined);
              setParam("min_confidence", undefined);
              setParam("persona", "");
            }}
          >
            Clear view filters
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <div className="grid grid-cols-12 gap-2 border-b bg-background px-4 py-2 text-xs font-medium text-muted-foreground">
          <div className="col-span-6">Summary</div>
          <div className="col-span-2">Saturation</div>
          <div className="col-span-2">Confidence</div>
          <div className="col-span-2">Risk hint</div>
        </div>

        <div className="divide-y">
          {rows.map((it: TopPain) => (
            <div
              key={it.cluster_id}
              className="grid grid-cols-12 gap-2 px-4 py-3 hover:bg-muted/40 cursor-pointer"
              onClick={() => update({ inspect: it.cluster_id })}
            >
              <div className="col-span-6 min-w-0">
                <div className="truncate text-sm font-medium">
                  {it.cluster_summary ?? "—"}
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  <span>id: {it.cluster_id}</span>
                  <Badge>{it.opportunity_window_status}</Badge>
                  <Badge>{it.dominant_persona}</Badge>
                  {it.vertical_id ? <Badge>{it.vertical_id}</Badge> : null}
                  <Link
                    href={`/clusters/${encodeURIComponent(it.cluster_id)}`}
                    className="underline underline-offset-2"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Deep dive
                  </Link>
                </div>
              </div>

              <div className="col-span-2 text-sm tabular-nums">
                <Badge>{String(it.saturation_score)}</Badge>
              </div>
              <div className="col-span-2 text-sm tabular-nums">{it.confidence_score}</div>
              <div className="col-span-2 text-xs text-muted-foreground">
                {riskHint(it)}
              </div>
            </div>
          ))}

          {rows.length === 0 && (
            <div className="px-4 py-6 text-sm text-muted-foreground">
              No declining clusters match current filters.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
