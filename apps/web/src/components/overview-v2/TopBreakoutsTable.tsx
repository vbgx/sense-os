"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export type BreakoutItem = {
  rank?: number;
  cluster_id: string;

  vertical_id?: string | null;
  vertical_label?: string | null;

  cluster_summary?: string | null;

  score?: number | null;
  breakout_score?: number | null;
  exploitability_score?: number | null;
  confidence_score?: number | null;

  tier?: string | null;
  status?: string | null;
  momentum_7d?: number | null;
};

type Props = {
  items: BreakoutItem[];
  subtitle?: string;
  note?: string;
};

type SortKey = "score" | "momentum_7d" | "confidence_score" | "rank";
type SortDir = "desc" | "asc";

function num(x: unknown): number {
  return typeof x === "number" && Number.isFinite(x) ? x : 0;
}

function fmtRank(x?: number) {
  const n = typeof x === "number" && Number.isFinite(x) ? x : 0;
  const s = String(n);
  return s.length >= 2 ? s : `0${s}`;
}

function fmtScore(x?: number | null) {
  if (x === null || x === undefined) return "—";
  if (!Number.isFinite(x)) return "—";
  return x.toFixed(0);
}

function fmtDelta(x?: number | null) {
  if (x === null || x === undefined) return "—";
  const sign = x > 0 ? "+" : "";
  return `${sign}${x.toFixed(0)}%`;
}

function deltaTone(x?: number | null) {
  if (x === null || x === undefined) return "text-muted-foreground";
  if (x > 0) return "text-emerald-300";
  if (x < 0) return "text-rose-300";
  return "text-muted-foreground";
}

function tierPill(tier?: string | null) {
  const t = (tier ?? "").toLowerCase();
  if (!t) return "—";
  return tier!;
}

function statusPill(status?: string | null) {
  const s = (status ?? "").toLowerCase();
  if (!s) return null;

  if (s.includes("hot") || s.includes("breakout")) return { label: "🔥 Hot", cls: "border-orange-400/30 text-orange-200" };
  if (s.includes("emerg")) return { label: "🌱 Emerging", cls: "border-emerald-400/30 text-emerald-200" };
  if (s.includes("stable")) return { label: "🟢 Stable", cls: "border-white/15 text-white/75" };
  if (s.includes("satur")) return { label: "⚠ Saturated", cls: "border-amber-400/30 text-amber-200" };
  if (s.includes("declin")) return { label: "❄ Declining", cls: "border-sky-400/30 text-sky-200" };

  return { label: status!, cls: "border-white/15 text-muted-foreground" };
}

export function TopBreakoutsTable({
  items,
  subtitle = "Ranked by opportunity score × momentum (live)",
  note = "“3 verticals entered HOT status in the last 24h.”",
}: Props) {
  const router = useRouter();
  const [sortKey, setSortKey] = useState<SortKey>("score");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const sorted = useMemo(() => {
    const arr = [...items];
    const dir = sortDir === "desc" ? -1 : 1;

    arr.sort((a, b) => {
      if (sortKey === "rank") return (num(a.rank) - num(b.rank)) * dir;

      const av = sortKey === "score" ? num(a.score ?? a.breakout_score ?? a.exploitability_score) : num(a[sortKey]);
      const bv = sortKey === "score" ? num(b.score ?? b.breakout_score ?? b.exploitability_score) : num(b[sortKey]);
      if (av !== bv) return (av - bv) * dir;

      // tie-breakers
      const s1 = num(a.score) - num(b.score);
      if (s1 !== 0) return s1 * -1;
      const m1 = num(a.momentum_7d) - num(b.momentum_7d);
      if (m1 !== 0) return m1 * -1;
      const c1 = num(a.confidence_score) - num(b.confidence_score);
      if (c1 !== 0) return c1 * -1;

      return (num(a.rank) - num(b.rank)) * 1;
    });

    return arr;
  }, [items, sortKey, sortDir]);

  return (
    <section className="rounded-2xl border bg-card/40 shadow-sm">
      <header className="flex items-baseline justify-between gap-3 border-b px-4 py-3">
        <div className="flex flex-col gap-0.5">
          <div className="text-[13px] font-semibold tracking-tight">Top 10 Breakouts</div>
          <div className="text-xs text-muted-foreground">{subtitle}</div>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden max-w-[420px] truncate font-mono text-xs text-muted-foreground lg:block">
            {note}
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="font-mono text-xs">
                Sort
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => { setSortKey("score"); setSortDir("desc"); }}>Score ↓</DropdownMenuItem>
              <DropdownMenuItem onClick={() => { setSortKey("momentum_7d"); setSortDir("desc"); }}>Δ 7d ↓</DropdownMenuItem>
              <DropdownMenuItem onClick={() => { setSortKey("confidence_score"); setSortDir("desc"); }}>Confidence ↓</DropdownMenuItem>
              <DropdownMenuItem onClick={() => { setSortKey("rank"); setSortDir("asc"); }}>Rank ↑</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <div className="px-4 py-3 pt-2">
        {sorted.length === 0 ? (
          <div className="rounded-2xl border bg-background/20 p-3">
            <div className="text-xs text-muted-foreground">No breakouts available.</div>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border">
            <table className="w-full min-w-[860px] border-collapse text-sm">
              <thead className="bg-background/20">
                <tr className="text-left font-mono text-[11px] text-muted-foreground">
                  <th className="w-[56px] px-3 py-2">Rank</th>
                  <th className="px-3 py-2">Vertical</th>
                  <th className="px-3 py-2 text-right">Score</th>
                  <th className="px-3 py-2 text-right">Δ 7d</th>
                  <th className="px-3 py-2 text-right">Confidence</th>
                  <th className="px-3 py-2">Tier</th>
                  <th className="px-3 py-2">Status</th>
                </tr>
              </thead>

              <tbody>
                {sorted.slice(0, 10).map((it, idx) => {
                  const status = statusPill(it.status);
                  const score = it.score ?? it.breakout_score ?? it.exploitability_score ?? null;
                  const shownRank = it.rank ?? idx + 1;

                  return (
                    <tr
                      key={it.cluster_id}
                      className="cursor-pointer border-t hover:bg-background/20"
                      onClick={() => router.push(`/clusters/${it.cluster_id}`)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") router.push(`/clusters/${it.cluster_id}`);
                      }}
                    >
                      <td className="px-3 py-2 font-mono text-xs text-muted-foreground">{fmtRank(shownRank)}</td>

                      <td className="px-3 py-2">
                        <div className="flex flex-col gap-0.5">
                          <div className="font-medium">
                            {it.vertical_label?.trim()?.length
                              ? it.vertical_label
                              : it.cluster_summary?.trim()?.length
                                ? it.cluster_summary
                                : `Cluster ${it.cluster_id}`}
                          </div>
                          <div className="font-mono text-[11px] text-muted-foreground/80">
                            {[
                              it.vertical_id ? `vertical=${it.vertical_id}` : null,
                              it.cluster_id ? `cluster=${it.cluster_id}` : null,
                            ]
                              .filter(Boolean)
                              .join(" · ")}
                          </div>
                        </div>
                      </td>

                      <td className="px-3 py-2 text-right font-mono font-semibold tabular-nums">{fmtScore(score)}</td>

                      <td className={cn("px-3 py-2 text-right font-mono tabular-nums", deltaTone(it.momentum_7d))}>
                        {fmtDelta(it.momentum_7d)}
                      </td>

                      <td className="px-3 py-2 text-right font-mono tabular-nums">
                        {it.confidence_score === null || it.confidence_score === undefined ? "—" : it.confidence_score.toFixed(2)}
                      </td>

                      <td className="px-3 py-2">
                        <span className="inline-flex rounded-full border bg-background/10 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                          {tierPill(it.tier)}
                        </span>
                      </td>

                      <td className="px-3 py-2">
                        {status ? (
                          <span className={cn("inline-flex items-center rounded-full border bg-background/10 px-2 py-0.5 font-mono text-[11px]", status.cls)}>
                            {status.label}
                          </span>
                        ) : (
                          <span className="font-mono text-[11px] text-muted-foreground">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
