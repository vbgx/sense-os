"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Activity, Radar, TrendingDown, Layers3, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { Separator } from "@/components/ui/separator";

const items = [
  { href: "/overview", label: "Overview", icon: BarChart3 },
  { href: "/opportunities", label: "Opportunities", icon: Layers3 },
  { href: "/verticals", label: "Verticals", icon: Activity },
  { href: "/emerging", label: "Emerging", icon: Radar },
  { href: "/declining", label: "Declining", icon: TrendingDown },
  { href: "/analytics", label: "Analytics", icon: ShieldCheck },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 h-screen w-64 border-r bg-background">
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold">Sense-OS</div>
          <div className="text-xs text-muted-foreground">Console</div>
        </div>
      </div>

      <Separator />

      <nav className="p-2">
        <div className="space-y-1">
          {items.map((it) => {
            const active = pathname === it.href || pathname.startsWith(it.href + "/");
            const Icon = it.icon;
            return (
              <Link
                key={it.href}
                href={it.href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm",
                  "hover:bg-muted",
                  active && "bg-muted"
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{it.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </aside>
  );
}
