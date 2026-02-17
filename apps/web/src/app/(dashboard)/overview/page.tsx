"use client";

import { useTopPains } from "@/lib/api/queries";
import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/Skeleton";

export default function Page() {
  const { state, update, reset } = useDashboardQueryState();

  const q = useTopPains({
    limit: state.limit,
    offset: state.offset,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Overview</h1>
          <p className="text-sm text-muted-foreground">
            Market snapshot (URL-synced)
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={reset}>
          Reset filters
        </Button>
      </div>

      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => update({ sort: "score_desc", offset: 0 })}
        >
          Sort: Score ↓
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => update({ sort: "score_asc", offset: 0 })}
        >
          Sort: Score ↑
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() =>
            update({ offset: state.offset + state.limit })
          }
        >
          Next Page
        </Button>
      </div>

      {q.isLoading && (
        <div className="space-y-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      )}

      {q.data && (
        <div className="rounded-md border divide-y">
          {q.data.items.map((it) => (
            <div
              key={it.cluster_id}
              className="flex items-center justify-between px-4 py-3"
            >
              <div>
                <div className="text-sm font-medium">{it.title}</div>
                <div className="text-xs text-muted-foreground">
                  id: {it.cluster_id}
                </div>
              </div>
              <div className="text-sm tabular-nums">
                {it.score.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
