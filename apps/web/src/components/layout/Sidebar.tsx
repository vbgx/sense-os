"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";
import { fetchJson } from "@/lib/api/client";
import { useQuery } from "@tanstack/react-query";

type MetaStatusOut = {
  status: string;
  last_run_at: string | null;
  scoring_version: string;
  total_signals_7d: number;
  total_clusters: number;
};

function pill(v: string | number | null | undefined) {
  if (v === null || v === undefined) return "—";
  return String(v);
}

function useMetaStatus() {
  return useQuery({
    queryKey: ["meta", "status"],
    queryFn: () => fetchJson<MetaStatusOut>("/meta/status"),
    staleTime: 30_000,
  });
}

export function Sidebar() {
  const pathname = usePathname();
  const metaQ = useMetaStatus();

  const livePill = metaQ.data?.status?.toUpperCase() === "OK" ? "LIVE" : "LIVE";
  const clusters = metaQ.data?.total_clusters ?? null;
  const signals7d = metaQ.data?.total_signals_7d ?? null;

  const nav = [
    { href: "/overview", label: "Overview", pill: livePill },
    { href: "/live", label: "Live Opportunities", pill: "10" },
    { href: "/verticals", label: "Verticals", pill: pill(signals7d ? `${Math.round(signals7d / 10)}+` : "—") }, // proxy until endpoint exists
    { href: "/clusters", label: "Clusters", pill: pill(clusters) },
    { href: "/portfolio", label: "Portfolio", pill: "—" },
    { href: "/watchlist", label: "Watchlist", pill: "—" },
    { href: "/export", label: "Exports", pill: "v1" },
  ];

  return (
    <aside className="border-r border-white/10 bg-black/10 p-[18px] sticky top-0 h-screen">
      <div className="mb-3 border-b border-white/10 px-2 pb-3">
        <div className="flex items-center gap-3">
          <div className="h-[10px] w-[10px] rounded-full bg-gradient-to-b from-orange-500 to-emerald-400 shadow-[0_0_0_3px_rgba(255,255,255,.06)]" />
          <div>
            <div className="text-sm font-extrabold tracking-[.10em]">SENSE OS</div>
            <div className="mt-0.5 font-mono text-xs text-muted-foreground">v2 · dashboard</div>
          </div>
        </div>
      </div>

      <nav className="flex flex-col gap-1 px-2">
        {nav.map((it) => {
          const active = pathname === it.href || (it.href !== "/" && pathname?.startsWith(it.href));
          return (
            <Link
              key={it.href}
              href={it.href}
              className={cn(
                "flex items-center justify-between rounded-xl border px-3 py-2 text-sm",
                active
                  ? "border-white/15 bg-white/5 text-white/90"
                  : "border-transparent text-muted-foreground hover:border-white/10 hover:bg-white/5 hover:text-white/85"
              )}
            >
              <span>{it.label}</span>
              <span className="rounded-full border border-white/10 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                {it.pill}
              </span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-4 px-2">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground">
            <span className="relative inline-block h-2 w-2">
              <span className="sense-led-pulse absolute inset-0 rounded-full bg-emerald-400" />
              <span className="absolute inset-0 rounded-full bg-emerald-400" />
            </span>
            <span>{metaQ.isFetching ? "Refreshing…" : "Live"}</span>
            <span className="text-muted-foreground/60">·</span>
            <span className="truncate">{metaQ.data?.scoring_version ? `v${metaQ.data.scoring_version}` : "v—"}</span>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            {metaQ.data?.last_run_at ? (
              <span className="font-mono text-[11px]">last_run_at={new Date(metaQ.data.last_run_at).toLocaleString()}</span>
            ) : (
              <span className="font-mono text-[11px]">last_run_at=—</span>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
