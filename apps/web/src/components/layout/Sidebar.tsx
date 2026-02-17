"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

type NavItem = {
  label: string;
  href: string;
  pill?: string;
};

const NAV: NavItem[] = [
  { label: "Overview", href: "/overview", pill: "LIVE" },
  { label: "Live Opportunities", href: "/live", pill: "10" },
  { label: "Verticals", href: "/verticals", pill: "1.2k" },
  { label: "Clusters", href: "/clusters", pill: "312" },
  { label: "Portfolio", href: "/portfolio", pill: "—" },
  { label: "Watchlist", href: "/watchlist", pill: "6" },
  { label: "Exports", href: "/export", pill: "v1" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 h-screen w-[260px] border-r bg-black/20 px-4 py-5">
      {/* Brand */}
      <div className="mb-4 border-b pb-4">
        <div className="flex items-center gap-3">
          <div className="h-2.5 w-2.5 rounded-full bg-gradient-to-b from-orange-500 to-emerald-400 shadow-[0_0_0_3px_rgba(255,255,255,.06)]" />
          <div>
            <div className="text-sm font-bold tracking-[0.6px]">SENSE OS</div>
            <div className="font-mono text-[11px] text-muted-foreground">
              v2 · overview
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-2">
        {NAV.map((item) => {
          const active =
            pathname === item.href ||
            (item.href !== "/" && pathname?.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center justify-between rounded-xl border px-3 py-2 text-sm transition",
                active
                  ? "border-white/20 bg-white/5 text-white"
                  : "border-transparent text-muted-foreground hover:border-white/10 hover:bg-white/5 hover:text-white"
              )}
            >
              <span>{item.label}</span>

              {item.pill && (
                <span className="rounded-full border px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                  {item.pill}
                </span>
              )}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
