"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { EmptyBlock } from "@/components/ui/EmptyBlock";
import { Button } from "@/components/ui/button";
import { useWatchlist } from "@/lib/state/watchlist";
import { cn } from "@/lib/utils";

type Status = "hot" | "emerging" | "stable" | "saturated" | "declining";

type Row = {
  id: string; // vertical_id (v1)
  title: string;
  reason: string;
  score: number;
  delta7d: number;
  confidence: number;
  tier: string;
  status: Status;
  updated: string; // "2m"
};

type AlertFlag = "up" | "down" | "warn";

type Alert = {
  id: string;
  title: string;
  flag: AlertFlag;
  message: string;
};

function statusBadge(status: Status) {
  switch (status) {
    case "hot":
      return "🔥 Hot";
    case "emerging":
      return "🌱 Emerging";
    case "stable":
      return "🟢 Stable";
    case "saturated":
      return "⚠ Saturated";
    case "declining":
      return "❄ Declining";
  }
}

function statusClass(status: Status) {
  switch (status) {
    case "hot":
      return "border-[rgba(255,107,61,.35)] bg-[rgba(255,107,61,.10)] text-[rgba(255,200,185,1)]";
    case "emerging":
      return "border-[rgba(39,209,127,.35)] bg-[rgba(39,209,127,.08)] text-[rgba(153,255,205,1)]";
    case "stable":
      return "border-[rgba(255,255,255,.14)] bg-[rgba(255,255,255,.03)] text-[rgba(255,255,255,.75)]";
    case "saturated":
      return "border-[rgba(255,191,60,.35)] bg-[rgba(255,191,60,.08)] text-[rgba(255,221,156,1)]";
    case "declining":
      return "border-[rgba(138,164,255,.35)] bg-[rgba(138,164,255,.08)] text-[rgba(201,212,255,1)]";
  }
}

function flagClass(flag: AlertFlag) {
  switch (flag) {
    case "up":
      return "border-[rgba(39,209,127,.30)] bg-[rgba(39,209,127,.07)] text-[rgba(153,255,205,1)]";
    case "down":
      return "border-[rgba(255,90,122,.30)] bg-[rgba(255,90,122,.07)] text-[rgba(255,195,210,1)]";
    case "warn":
      return "border-[rgba(255,191,60,.30)] bg-[rgba(255,191,60,.07)] text-[rgba(255,221,156,1)]";
  }
}

function fmtDelta(x: number) {
  const sign = x >= 0 ? "+" : "";
  return `${sign}${x.toFixed(0)}%`;
}

const MOCK_ROWS: Row[] = [
  {
    id: "vert_healthcare_ops",
    title: "B2B Ops → Healthcare",
    reason: "watch reason: breakout signals + low heat",
    score: 81,
    delta7d: 18,
    confidence: 0.83,
    tier: "core",
    status: "hot",
    updated: "2m",
  },
  {
    id: "vert_cicd_security",
    title: "DevTools → CI/CD Security",
    reason: "watch reason: emerging + high exploitability",
    score: 78,
    delta7d: 11,
    confidence: 0.79,
    tier: "core",
    status: "emerging",
    updated: "6m",
  },
  {
    id: "vert_ar_automation",
    title: "B2B Finance → AR Automation",
    reason: "watch reason: stable cashflow pain + low heat",
    score: 75,
    delta7d: 9,
    confidence: 0.74,
    tier: "experimental",
    status: "stable",
    updated: "12m",
  },
  {
    id: "vert_seo_ops",
    title: "Marketing → SEO Content Ops",
    reason: "watch reason: declining risk + saturation check",
    score: 66,
    delta7d: -6,
    confidence: 0.68,
    tier: "experimental",
    status: "declining",
    updated: "18m",
  },
  {
    id: "vert_habit_tracking",
    title: "B2C Fitness → Habit Tracking",
    reason: "watch reason: saturated → monitor for reversal",
    score: 69,
    delta7d: -3,
    confidence: 0.71,
    tier: "long_tail",
    status: "saturated",
    updated: "23m",
  },
];

const MOCK_ALERTS: Alert[] = [
  {
    id: "a1",
    title: "B2B Ops → Healthcare",
    flag: "up",
    message: "Recurrence rising + competitive heat stable → candidate for bet slip.",
  },
  {
    id: "a2",
    title: "Marketing → SEO Content Ops",
    flag: "down",
    message: "Mentions now reference many existing tools → saturation likely increasing.",
  },
  {
    id: "a3",
    title: "B2C Fitness → Habit Tracking",
    flag: "warn",
    message: "If competition cools down, this could flip back to stable.",
  },
];

type SortKey = "delta" | "score" | "confidence" | "updated";

export default function Page() {
  const w = useWatchlist();

  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortKey>("delta");
  const [statusFilter, setStatusFilter] = useState<Status | "all">("all");
  const [alertsOnly, setAlertsOnly] = useState(true);
  const [minConfidence, setMinConfidence] = useState(0.75);

  const baseRows = useMemo(() => {
    // v1: if watchlist empty, render empty state (real behavior)
    // v1: if watchlist has items, we still render mock rows, but we ALSO allow unstar action.
    // (Later: we’ll map ids -> real rows via API.)
    if (w.count === 0) return [];
    return MOCK_ROWS.filter((r) => w.isStarred(r.id));
  }, [w.count, w.isStarred]);

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();

    let out = baseRows;

    if (q) {
      out = out.filter((r) => r.title.toLowerCase().includes(q) || r.reason.toLowerCase().includes(q));
    }

    if (statusFilter !== "all") {
      out = out.filter((r) => r.status === statusFilter);
    }

    out = out.filter((r) => r.confidence >= minConfidence);

    if (alertsOnly) {
      const titles = new Set(MOCK_ALERTS.map((a) => a.title));
      out = out.filter((r) => titles.has(r.title));
    }

    const updatedRank = (s: string) => {
      // "2m" -> 2 ; "12m" -> 12 ; fallback large
      const m = s.match(/^(\d+)\s*m$/i);
      return m ? Number(m[1]) : 9999;
    };

    const sorters: Record<SortKey, (a: Row, b: Row) => number> = {
      delta: (a, b) => b.delta7d - a.delta7d,
      score: (a, b) => b.score - a.score,
      confidence: (a, b) => b.confidence - a.confidence,
      updated: (a, b) => updatedRank(a.updated) - updatedRank(b.updated), // recent first (smaller is newer)
    };

    return [...out].sort(sorters[sort]);
  }, [alertsOnly, baseRows, minConfidence, query, sort, statusFilter]);

  if (w.count === 0) {
    return (
      <div className="space-y-4">
        <EmptyBlock
          title="Watchlist is empty"
          description="Star a vertical to monitor it (early warning system). Watchlist ≠ Portfolio."
          onAction={() => {
            // no-op: keep it simple (UI-only)
          }}
          actionLabel="Add first star"
        />
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="secondary">
            <Link href="/overview">Go to Overview</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/verticals">Browse Verticals</Link>
          </Button>
        </div>

        <div className="sense-panel rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="text-xs font-semibold text-white/90">Quick seed (dev)</div>
          <div className="mt-1 text-xs text-muted-foreground">
            For now, star these mock verticals from the Overview / Verticals UI. (Next: add star toggle there.)
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header (matches your mock vibe) */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-white/90">Watchlist</h1>
          <p className="mt-1 max-w-[940px] text-sm text-muted-foreground">
            Your monitored opportunities. Watch score deltas, confidence drift, and trend shifts. This is your “early warning
            system” before committing in VentureOS.
          </p>
        </div>

        <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-3 py-2">
          <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground">
            <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_0_3px_rgba(39,209,127,.18)]" />
            <span>Live</span>
            <span className="text-white/30">·</span>
            <span>Updated 2m ago</span>
          </div>
          <button
            type="button"
            className="rounded-xl border border-white/10 bg-white/5 px-2.5 py-1.5 font-mono text-xs text-white/80 hover:border-white/20 hover:bg-white/10"
          >
            Refresh
          </button>
        </div>
      </div>

      <section className="sense-panel rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-white/[0.03] shadow-[0_14px_50px_rgba(0,0,0,.55)]">
        <div className="flex flex-wrap items-start justify-between gap-3 border-b border-white/10 px-4 py-3">
          <div>
            <div className="text-sm font-semibold text-white/90">Monitored Verticals</div>
            <div className="mt-0.5 text-xs text-muted-foreground">Sort by delta to surface the biggest changes first.</div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-black/20 px-3 py-2">
              <span className="font-mono text-xs text-white/40">⌕</span>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search watchlist..."
                className="w-[260px] bg-transparent text-sm text-white/90 outline-none placeholder:text-white/30"
              />
            </div>

            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as SortKey)}
              className="rounded-2xl border border-white/10 bg-black/20 px-3 py-2 font-mono text-xs text-muted-foreground outline-none"
            >
              <option value="delta">Sort: Δ 7d desc</option>
              <option value="score">Score desc</option>
              <option value="confidence">Confidence desc</option>
              <option value="updated">Updated recent</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Status | "all")}
              className="rounded-2xl border border-white/10 bg-black/20 px-3 py-2 font-mono text-xs text-muted-foreground outline-none"
            >
              <option value="all">Status: all</option>
              <option value="hot">🔥 Hot</option>
              <option value="emerging">🌱 Emerging</option>
              <option value="stable">🟢 Stable</option>
              <option value="saturated">⚠ Saturated</option>
              <option value="declining">❄ Declining</option>
            </select>

            <button
              type="button"
              onClick={() => setAlertsOnly((x) => !x)}
              className={cn(
                "rounded-2xl border px-3 py-2 font-mono text-xs",
                alertsOnly
                  ? "border-[rgba(255,107,61,.35)] bg-[rgba(255,107,61,.12)] text-white/90"
                  : "border-white/10 bg-white/5 text-muted-foreground hover:border-white/20 hover:bg-white/10"
              )}
            >
              Show alerts only
            </button>

            <button
              type="button"
              onClick={() => setMinConfidence((x) => (x === 0.75 ? 0 : 0.75))}
              className={cn(
                "rounded-2xl border px-3 py-2 font-mono text-xs",
                minConfidence >= 0.75
                  ? "border-[rgba(255,107,61,.35)] bg-[rgba(255,107,61,.12)] text-white/90"
                  : "border-white/10 bg-white/5 text-muted-foreground hover:border-white/20 hover:bg-white/10"
              )}
            >
              Confidence ≥ 0.75
            </button>
          </div>
        </div>

        <div className="grid gap-3 p-4 lg:grid-cols-[1.25fr_.75fr]">
          {/* LEFT table */}
          <div className="rounded-2xl border border-white/10 bg-transparent">
            <div className="overflow-hidden rounded-2xl">
              <div className="grid grid-cols-12 gap-0 border-b border-white/10 px-3 py-3 font-mono text-[11px] text-white/45">
                <div className="col-span-5">Vertical</div>
                <div className="col-span-1 text-right">Score</div>
                <div className="col-span-2 text-right">Δ 7d</div>
                <div className="col-span-2 text-right">Confidence</div>
                <div className="col-span-1">Tier</div>
                <div className="col-span-1">Status</div>
              </div>

              <div className="divide-y divide-white/10">
                {rows.map((r) => (
                  <div key={r.id} className="grid grid-cols-12 items-center gap-0 px-3 py-3 hover:bg-white/[0.03]">
                    <div className="col-span-5">
                      <Link href={`/verticals/${encodeURIComponent(r.id)}`} className="block">
                        <div className="flex items-center gap-2">
                          <div className="text-sm font-medium text-white/90 hover:underline">{r.title}</div>
                        </div>
                        <div className="mt-0.5 font-mono text-[11px] text-white/45">{r.reason}</div>
                      </Link>
                    </div>

                    <div className="col-span-1 text-right font-mono text-sm font-extrabold text-white/80">{r.score}</div>

                    <div
                      className={cn(
                        "col-span-2 text-right font-mono text-sm",
                        r.delta7d >= 0 ? "text-emerald-300" : "text-rose-300"
                      )}
                    >
                      {fmtDelta(r.delta7d)}
                    </div>

                    <div className="col-span-2 text-right font-mono text-sm text-white/70">{r.confidence.toFixed(2)}</div>

                    <div className="col-span-1">
                      <span className="inline-flex rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono text-[11px] text-white/45">
                        {r.tier}
                      </span>
                    </div>

                    <div className="col-span-1 flex items-center justify-between gap-2">
                      <span className={cn("inline-flex rounded-full border px-2 py-0.5 font-mono text-[11px]", statusClass(r.status))}>
                        {statusBadge(r.status)}
                      </span>

                      <button
                        type="button"
                        title="Unstar"
                        onClick={() => w.remove(r.id)}
                        className="ml-2 rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono text-[11px] text-white/60 hover:border-white/20 hover:bg-white/10"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT cards */}
          <div className="grid gap-3">
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <div className="text-sm font-semibold text-white/90">Alerts</div>
              <div className="mt-1 text-xs text-muted-foreground">
                Automatic “watch reasons” that trigger when the opportunity changes materially.
              </div>

              <div className="mt-3 grid gap-2">
                {MOCK_ALERTS.map((a) => (
                  <div key={a.id} className="rounded-2xl border border-white/10 bg-white/[0.02] p-3">
                    <div className="flex items-center justify-between gap-2 font-mono text-[11px] text-white/45">
                      <span>{a.title}</span>
                      <span className={cn("inline-flex rounded-full border px-2 py-0.5", flagClass(a.flag))}>
                        {a.flag === "up" ? "momentum spike" : a.flag === "down" ? "confidence drift" : "watch reversal"}
                      </span>
                    </div>
                    <div className="mt-2 text-sm text-white/80">{a.message}</div>
                  </div>
                ))}
              </div>

              <button
                type="button"
                className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-white/80 hover:border-white/20 hover:bg-white/10"
              >
                ⚙ Manage Alert Rules
              </button>
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <div className="text-sm font-semibold text-white/90">Notes</div>
              <div className="mt-1 text-xs text-muted-foreground">
                Human intent matters. Add a note to remember why you’re tracking something.
              </div>

              <div className="mt-3 rounded-2xl border border-white/10 bg-white/[0.02] p-3">
                <div className="flex items-center justify-between gap-2 font-mono text-[11px] text-white/45">
                  <span>Note (example)</span>
                  <span className="inline-flex rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5">private</span>
                </div>
                <div className="mt-2 text-sm text-white/80">
                  “If Healthcare ops remains Hot for 2 weeks → create VentureOS bet slip and start 10 interviews.”
                </div>
              </div>

              <button
                type="button"
                className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-white/80 hover:border-white/20 hover:bg-white/10"
              >
                ＋ Add Note
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
