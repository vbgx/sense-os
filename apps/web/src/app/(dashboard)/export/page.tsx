"use client";

import { EmptyBlock } from "@/components/ui/EmptyBlock";

export default function Page() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-xl font-semibold">Export</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Export VentureOS payloads for clusters (JSON).
        </div>
      </div>

      <EmptyBlock
        title="Nothing to export"
        description="Open a cluster and use the Export action to generate a payload."
      />
    </div>
  );
}
