"use client";

import { Button } from "@/components/ui/button";

type Props = {
  updatedLabel: string;
  onRefresh: () => void;
  isRefreshing?: boolean;
};

export function OverviewHeader({ updatedLabel, onRefresh, isRefreshing }: Props) {
  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <div className="text-xl font-semibold">Overview</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Market snapshot • last refreshed: {updatedLabel}
        </div>
      </div>

      <Button onClick={onRefresh} disabled={Boolean(isRefreshing)}>
        {isRefreshing ? "Refreshing…" : "Refresh"}
      </Button>
    </div>
  );
}
