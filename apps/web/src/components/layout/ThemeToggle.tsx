"use client";

import { useEffect, useMemo, useState } from "react";
import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { theme, systemTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const resolved = useMemo(() => {
    if (theme === "system") return systemTheme;
    return theme;
  }, [theme, systemTheme]);

  if (!mounted) {
    // Avoid hydration mismatch
    return (
      <Button variant="outline" size="sm" className="gap-2" aria-label="Toggle theme" disabled>
        <span className="h-4 w-4" />
        <span className="text-xs">Theme</span>
      </Button>
    );
  }

  const isDark = resolved === "dark";
  const next = isDark ? "light" : "dark";

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={() => setTheme(next)}
      className="gap-2"
      aria-label="Toggle theme"
    >
      {isDark ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
      <span className="text-xs">Theme</span>
    </Button>
  );
}
