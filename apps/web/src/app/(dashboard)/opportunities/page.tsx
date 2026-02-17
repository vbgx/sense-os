"use client";

import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { useTopPains } from "@/lib/api/queries";
import { OpportunityTable } from "@/components/opportunity/OpportunityTable";
import { ClusterInspectDrawer } from "@/components/opportunity/ClusterInspectDrawer";
import { Skeleton } from "@/components/ui/Skeleton";

export default function Page() {
  const { state, update } = useDashboardQueryState();

  const q = useTopPains({
    limit: state.limit,
    offset: state.offset,
    vertical_id: state.vertical_id,
    tier: state.tier,
    emerging_only: state.emerging_only,
  });

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Opportunities</h1>

      {q.isLoading && <Skeleton className="h-[600px] w-full" />}

      {q.isError && (
        <div className="rounded-md border p-3">
          <div className="text-sm font-medium">API error</div>
          <div className="mt-1 text-xs text-muted-foreground">
            {q.error instanceof Error ? q.error.message : "Unknown error"}
          </div>
        </div>
      )}

      {q.data && (
        <OpportunityTable
          data={q.data}
          onRowClick={(clusterId) => update({ inspect: clusterId })}
        />
      )}

      <ClusterInspectDrawer />
    </div>
  );
}
