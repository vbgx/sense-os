"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { useTopPains, useTrending, useVerticals } from "@/lib/api/queries";
import { fetchJson } from "@/lib/api/client";
import { getErrorMessage } from "@/lib/utils/getErrorMessage";
import { Skeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/button";
import { VerticalTrendChart } from "@/components/vertical/VerticalTrendChart";
import { VerticalTierDistribution } from "@/components/vertical/VerticalTierDistribution";
import { OpportunityTable } from "@/components/opportunity/OpportunityTable";

export default function Page() {
  const params = useParams<{ vertical_id: string }>();
  const verticalIdStr = params.vertical_id;
  const verticalIdNum = Number(verticalIdStr);
  const verticalIdOk = Number.isFinite(verticalIdNum) && verticalIdNum >= 1;

  const vq = useVerticals();
  const [exporting, setExporting] = useState(false);

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

  const vertical = useMemo(() => {
    return (vq.data ?? []).find((x) => String(x.id) === String(verticalIdStr));
  }, [vq.data, verticalIdStr]);

  const name = vertical?.name ?? `Vertical ${verticalIdStr}`;
  const taxonomyVersion = vertical?.taxonomy_version ?? null;
  const metaLine = [vertical?.meta?.industry, vertical?.meta?.function].filter(Boolean).join(" • ");

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

  const handleExport = async () => {
    setExporting(true);
    try {
      const qs = new URLSearchParams();
      if (taxonomyVersion) qs.set("taxonomy_version", taxonomyVersion);
      const path = `/verticals/${encodeURIComponent(verticalIdStr)}/ventureos_export${
        qs.toString() ? `?${qs.toString()}` : ""
      }`;

      const payload = await fetchJson<unknown>(path);
      const fileName = `ventureos_${verticalIdStr}.json`;
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      link.click();
      URL.revokeObjectURL(url);
      toast.success("Export ready", { description: `Downloaded ${fileName}` });
    } catch (err) {
      toast.error("Export failed", { description: getErrorMessage(err) });
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xl font-semibold">{name}</div>
          <div className="mt-1 text-sm text-muted-foreground">id: {verticalIdStr}</div>
          {metaLine && <div className="mt-1 text-xs text-muted-foreground">{metaLine}</div>}
          {taxonomyVersion && (
            <div className="mt-1 text-xs text-muted-foreground">taxonomy: {taxonomyVersion}</div>
          )}
        </div>
        <Button onClick={handleExport} disabled={exporting}>
          {exporting ? "Exporting..." : "Export to VentureOS"}
        </Button>
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
