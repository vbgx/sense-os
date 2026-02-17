"use client";

import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { useTopPains } from "@/lib/api/queries";
import { OpportunityTable } from "@/components/opportunity/OpportunityTable";
import { Skeleton } from "@/components/ui/Skeleton";

export default function Page() {
  const { state } = useDashboardQueryState();

  const q = useTopPains({
    limit: state.limit,
    offset: state.offset,
    sort: state.sort,
    vertical: state.vertical,
  });

  if (q.isLoading) {
    return <Skeleton className="h-[600px] w-full" />;
  }

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

  if (!q.data) return null;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Opportunities</h1>
      <OpportunityTable data={q.data.items} />
    </div>
  );
}
