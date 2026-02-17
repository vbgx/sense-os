"use client";

import { EmptyBlock } from "@/components/ui/EmptyBlock";

export default function Page() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-xl font-semibold">Portfolio</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Your committed bets and active projects.
        </div>
      </div>

      <EmptyBlock
        title="No bets yet"
        description="When you commit on a cluster, it will appear here with a Bet Slip."
      />
    </div>
  );
}
