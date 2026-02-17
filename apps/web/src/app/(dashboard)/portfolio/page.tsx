"use client";

import Link from "next/link";
import { usePortfolio } from "@/lib/state/portfolio";
import { EmptyBlock } from "@/components/ui/EmptyBlock";
import { Button } from "@/components/ui/button";

function fmt(ts: number) {
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return "—";
  }
}

export default function Page() {
  const p = usePortfolio();

  if (p.count === 0) {
    return (
      <div className="space-y-3">
        <EmptyBlock
          title="Portfolio is empty"
          description="Tracked clusters will appear here. Use “Add to Portfolio” from a cluster deep dive or track from tables."
        />
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="secondary">
            <Link href="/overview">Go to Overview</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/clusters">Browse Clusters</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="sense-panel rounded-2xl border p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="text-xs text-muted-foreground">Act</div>
            <h1 className="text-xl font-semibold tracking-tight text-white/90">Portfolio</h1>
            <div className="mt-1 text-sm text-muted-foreground">
              Your conviction bets. Persisted locally (v1). No backend coupling.
            </div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-muted-foreground">
            tracked={p.count}
          </div>
        </div>
      </div>

      <div className="sense-panel overflow-hidden rounded-2xl border">
        <div className="grid grid-cols-12 gap-0 border-b border-white/10 px-4 py-3 text-[11px] font-mono text-muted-foreground">
          <div className="col-span-5">cluster</div>
          <div className="col-span-4">last change</div>
          <div className="col-span-3 text-right">actions</div>
        </div>

        <div className="divide-y divide-white/10">
          {p.items.map((it) => (
            <div key={it.cluster_id} className="grid grid-cols-12 items-center gap-0 px-4 py-3">
              <div className="col-span-5">
                <Link href={`/clusters/${encodeURIComponent(it.cluster_id)}`} className="group">
                  <div className="text-sm font-medium text-white/90 group-hover:underline">{it.cluster_id}</div>
                  <div className="mt-1 text-xs text-muted-foreground">status=tracked · v1</div>
                </Link>
              </div>

              <div className="col-span-4 font-mono text-xs text-muted-foreground">{fmt(it.added_at)}</div>

              <div className="col-span-3 flex justify-end gap-2">
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/clusters/${encodeURIComponent(it.cluster_id)}`}>Open</Link>
                </Button>
                <Button variant="secondary" size="sm" onClick={() => p.remove(it.cluster_id)}>
                  Remove
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

