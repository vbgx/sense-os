"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";

import { Button } from "@/components/ui/button";

function useIsClient() {
  return React.useSyncExternalStore(
    () => () => {},          // subscribe (no-op)
    () => true,              // client snapshot
    () => false              // server snapshot
  );
}

export function ThemeToggle() {
  const isClient = useIsClient();
  const { theme, setTheme, systemTheme } = useTheme();

  // Avoid hydration mismatch: don't read theme/systemTheme until client.
  const resolvedTheme = isClient ? (theme === "system" ? systemTheme : theme) : null;

  const nextTheme = resolvedTheme === "dark" ? "light" : "dark";

  return (
    <Button
      type="button"
      variant="outline"
      size="icon"
      onClick={() => setTheme(nextTheme)}
      aria-label="Toggle theme"
      disabled={!isClient}
    >
      {resolvedTheme === "dark" ? (
        <Sun className="h-4 w-4" />
      ) : (
        <Moon className="h-4 w-4" />
      )}
    </Button>
  );
}
