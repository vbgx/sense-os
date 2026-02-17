"use client";

import { useEffect } from "react";
import { toast } from "sonner";
import { ErrorState } from "@/components/ui/ErrorState";
import { getErrorMessage } from "@/lib/utils/getErrorMessage";

export default function Error({
  error,
  reset,
}: {
  error: unknown;
  reset: () => void;
}) {
  useEffect(() => {
    toast.error("Opportunities failed to load", {
      description: getErrorMessage(error),
    });
  }, [error]);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Opportunities</h1>
      <ErrorState
        title="Couldn’t load opportunities"
        description={getErrorMessage(error)}
        onRetry={reset}
      />
    </div>
  );
}
