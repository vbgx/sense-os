"use client";

import { useVerticals } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";
import { VerticalTable } from "@/components/vertical/VerticalTable";

export default function Page() {
  const q = useVerticals();

  if (q.isLoading) return <Skeleton className="h-[520px] w-full" />;

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

  return (
    <div className="space-y-4">
      <div>
        <div className="text-xl font-semibold">Verticals</div>
        <div className="mt-1 text-sm text-muted-foreground">Explorer • ranking (v0)</div>
      </div>

      <VerticalTable items={q.data ?? []} />
    </div>
  );
}
