"use client";

import { useMemo } from "react";
import { useParams } from "next/navigation";
import { useTopPains, useTrending, useVerticals } from "@/lib/api/queries";
import { Skeleton } from "@/components/ui/Skeleton";
import { VerticalTrendChart } from "@/components/vertical/VerticalTrendChart";
import { VerticalTierDistribution } from "@/components/vertical/VerticalTierDistribution";
import { OpportunityTable } from "@/components/opportunity/OpportunityTable";

export default function Page() {
  const params = useParams<{ vertical_id: string }>();
  const verticalIdStr = params.vertical_id;
  const verticalIdNum = Number(verticalIdStr);
  const verticalIdOk = Number.isFinite(verticalIdNum) && verticalIdNum >= 1;

  const vq = useVerticals();

  const topQ = useTopPains({
    vertical_id: verticalIdStr,
    limit: 50,
    offset: 0,
  });

  const trendingQ = useTrending({
    vertical_id: verticalIdOk ? verticalIdNum : 1,
    limit: 20,
    offset: 0,
    sparkline_days: 30,
    enabled: verticalIdOk,
  });

  const name = useMemo(() => {
    const v = (vq.data ?? []).find((x) => String(x.id) === String(verticalIdStr));
    return v?.name ?? `Vertical ${verticalIdStr}`;
  }, [vq.data, verticalIdStr]);

  const loading = topQ.isLoading || vq.isLoading || trendingQ.isLoading;
  if (loading) return <Skeleton className="h-[720px] w-full" />;

  if (topQ.isError || vq.isError || trendingQ.isError) {
    const err =
      (topQ.error instanceof Error && topQ.error.message) ||
      (vq.error instanceof Error && vq.error.message) ||
      (trendingQ.error instanceof Error && trendingQ.error.message) ||
      "Unknown error";

    return (
      <div className="rounded-md border p-3">
        <div className="text-sm font-medium">API error</div>
        <div className="mt-1 text-xs text-muted-foreground">{err}</div>
      </div>
    );
  }

  const top = topQ.data ?? [];
  const trending = trendingQ.data?.items ?? [];

  return (
    <div className="space-y-6">
      <div>
        <div className="text-xl font-semibold">{name}</div>
        <div className="mt-1 text-sm text-muted-foreground">id: {verticalIdStr}</div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <VerticalTrendChart items={trending} />
        <VerticalTierDistribution items={top} />
      </div>

      <div className="space-y-2">
        <div className="text-sm font-medium">Top clusters</div>
        <OpportunityTable data={top} />
      </div>
    </div>
  );
}
