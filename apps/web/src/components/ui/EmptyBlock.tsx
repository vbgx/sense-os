import React from "react";
import { Button } from "./button";

type Props = {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
  testId?: string;
};

export function EmptyBlock({
  title,
  description,
  actionLabel,
  onAction,
  className,
  testId,
}: Props) {
  return (
    <div
      data-testid={testId}
      className={[
        "rounded-xl border border-dashed p-8 text-center",
        "bg-background/40",
        className ?? "",
      ].join(" ")}
    >
      <div className="mx-auto max-w-md space-y-2">
        <h3 className="text-base font-semibold">{title}</h3>
        {description ? (
          <p className="text-sm text-muted-foreground">{description}</p>
        ) : null}

        {actionLabel && onAction ? (
          <div className="pt-3">
            <Button onClick={onAction} variant="secondary">
              {actionLabel}
            </Button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
