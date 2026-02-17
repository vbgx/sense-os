"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Something went wrong</h1>
      <p className="text-sm text-muted-foreground">
        The dashboard failed to load. Check API availability and try again.
      </p>
      <div className="rounded-md border p-3 text-xs text-muted-foreground">
        {error.message}
      </div>
      <Button variant="outline" onClick={() => reset()}>
        Retry
      </Button>
    </div>
  );
}
