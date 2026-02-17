"use client";

import { EmptyState } from "@/components/ui/EmptyState";

export default function Page() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-xl font-semibold">Live Opportunity</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Real-time opportunity feed (coming soon).
        </div>
      </div>

      <EmptyState
        title="Live feed not wired yet"
        description="We will connect this to streaming signals / latest clusters."
      />
    </div>
  );
}
