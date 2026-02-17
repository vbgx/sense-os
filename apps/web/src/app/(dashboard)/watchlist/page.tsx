"use client";

import { EmptyState } from "@/components/ui/EmptyState";

export default function Page() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-xl font-semibold">Watchlist</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Opportunities you are tracking over time.
        </div>
      </div>

      <EmptyState
        title="No items yet"
        description="Add a cluster to your watchlist from Overview or a Cluster page."
      />
    </div>
  );
}
