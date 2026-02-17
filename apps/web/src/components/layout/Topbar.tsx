"use client";

import { ThemeToggle } from "@/components/layout/ThemeToggle";

export function Topbar() {
  return (
    <header className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
      <div className="flex h-14 items-center justify-between px-6">
        <div className="text-sm text-muted-foreground">Market Snapshot</div>
        <ThemeToggle />
      </div>
    </header>
  );
}
