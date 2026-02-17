"use client";

import React from "react";
import { Button } from "./button";

type Props = {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
};

export function ErrorBlock({
  title = "Something went wrong",
  description = "We couldn’t load this view. Try again.",
  onRetry,
  className,
}: Props) {
  return (
    <div
      className={[
        "rounded-xl border p-8",
        "bg-background/40",
        className ?? "",
      ].join(" ")}
    >
      <div className="space-y-2">
        <h3 className="text-base font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>

        {onRetry ? (
          <div className="pt-3">
            <Button onClick={onRetry} variant="secondary">
              Retry
            </Button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
