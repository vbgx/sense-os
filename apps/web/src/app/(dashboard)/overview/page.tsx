"use client";

import Link from "next/link";
import { useTopPains } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";

export default function Page() {
  const q = useTopPains({ limit: 20, offset: 0 });

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <h1 className="text-xl font-semibold">Overview</h1>
        <p className="text-sm text-muted-foreground">Market snapshot (Top pains)</p>
      </div>

      {q.isLoading && (
        <div className="space-y-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      )}

      {q.isError && (
        <div className="rounded-md border p-3">
          <div className="text-sm font-medium">API error</div>
          <div className="mt-1 text-xs text-muted-foreground">
            {q.error instanceof Error ? q.error.message : "Unknown error"}
          </div>
        </div>
      )}

      {q.data && (
        <div className="rounded-md border">
          <div className="flex items-center justify-between border-b px-4 py-2">
            <div className="text-sm font-medium">Top pains</div>
            <div className="text-xs text-muted-foreground">
              {q.data.generated_at ? `generated_at: ${q.data.generated_at}` : ""}
            </div>
          </div>

          <div className="divide-y">
            {q.data.items.map((it) => (
              <div key={it.cluster_id} className="flex items-center justify-between px-4 py-3">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">{it.title}</div>
                  <div className="text-xs text-muted-foreground">
                    {it.vertical_id ? `vertical: ${it.vertical_id} • ` : ""}
                    id: {it.cluster_id}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-sm tabular-nums">{it.score.toFixed(2)}</div>
                  <Link
                    href={`/clusters/${encodeURIComponent(it.cluster_id)}`}
                    className="text-xs underline text-muted-foreground hover:text-foreground"
                  >
                    inspect
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
