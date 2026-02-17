"use client";

import { useEffect, useRef } from "react";
import { toast } from "sonner";

import { useDashboardQueryState } from "@/lib/state/useDashboardQueryState";
import { useTopPains } from "@/lib/api/queries";
import { OpportunityTable } from "@/components/opportunity/OpportunityTable";
import { ClusterInspectDrawer } from "@/components/opportunity/ClusterInspectDrawer";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import { getErrorMessage } from "@/lib/utils/getErrorMessage";

export default function Page() {
  const { state, update } = useDashboardQueryState();

  const q = useTopPains({
    limit: state.limit,
    offset: state.offset,
    vertical_id: state.vertical_id,
    tier: state.tier,
    emerging_only: state.emerging_only,
  });

  const hasToastedRef = useRef(false);

  useEffect(() => {
    if (!q.isError) {
      hasToastedRef.current = false;
      return;
    }
    if (hasToastedRef.current) return;

    hasToastedRef.current = true;
    toast.error("API error", { description: getErrorMessage(q.error) });
  }, [q.isError, q.error]);

  const resetFilters = () => {
    update({
      vertical_id: undefined,
      tier: undefined,
      emerging_only: undefined,
      offset: 0,
      inspect: undefined,
    });
  };

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Opportunities</h1>

      {q.isLoading && <Skeleton className="h-[600px] w-full" />}

      {q.isError && (
        <ErrorState
          title="Couldn’t load opportunities"
          description={getErrorMessage(q.error)}
          onRetry={() => q.refetch()}
        />
      )}

      {q.data && (
        <OpportunityTable
          data={q.data}
          onRowClick={(clusterId) => update({ inspect: clusterId })}
          onResetFilters={resetFilters}
        />
      )}

      <ClusterInspectDrawer />
    </div>
  );
}
