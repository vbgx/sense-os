"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "@/lib/api/client";

export type ClusterStatus = "HOT" | "EMERGING" | "STABLE" | "SATURATED" | "DECLINING" | "UNKNOWN";

export type ClusterScoreBreakdown = {
  severity: number;       // 0..100
  recurrence: number;     // 0..100
  exploitability: number; // 0..100
  competition: number;    // 0..100
  freshness: number;      // 0..100
};

export type TimelinePoint = {
  label: string;
  at: string;
  kind: "emerging" | "breakout" | "declining" | "info";
};

export type ClusterDetail = {
  id: string;

  title: string;
  subtitle: string;
  status: ClusterStatus;
  score: number;          // 0..100
  percentile: number;     // 0..100
  momentum_7d: number;    // -100..+100 (%)
  tier: string;
  confidence: number;     // 0..1

  why_now: string[];
  breakdown: ClusterScoreBreakdown;
  timeline: TimelinePoint[];
};

function isObj(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null;
}
function str(x: unknown, fallback = "—"): string {
  return typeof x === "string" && x.trim().length ? x : fallback;
}
function num(x: unknown, fallback = 0): number {
  return typeof x === "number" && Number.isFinite(x) ? x : fallback;
}
function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

function getNum(o: unknown, k: string, fallback: number) {
  if (!isObj(o)) return fallback;
  return num(o[k], fallback);
}

export function normalizeClusterDetail(id: string, raw: unknown): ClusterDetail {
  const base: ClusterDetail = {
    id,
    title: "—",
    subtitle: `cluster=${id}`,
    status: "UNKNOWN",
    score: 0,
    percentile: 0,
    momentum_7d: 0,
    tier: "—",
    confidence: 0,

    why_now: ["Waiting for data…", "API not connected or empty payload."],
    breakdown: { severity: 40, recurrence: 40, exploitability: 40, competition: 40, freshness: 40 },
    timeline: [
      { label: "Emerging", at: "—", kind: "info" },
      { label: "Breakout", at: "—", kind: "info" },
      { label: "Declining", at: "—", kind: "info" },
    ],
  };

  if (!isObj(raw)) return base;

  const statusRaw = str(raw.status, "UNKNOWN").toUpperCase();
  const status: ClusterStatus =
    statusRaw === "HOT" ? "HOT" :
    statusRaw === "EMERGING" ? "EMERGING" :
    statusRaw === "STABLE" ? "STABLE" :
    statusRaw === "SATURATED" ? "SATURATED" :
    statusRaw === "DECLINING" ? "DECLINING" :
    "UNKNOWN";

  const breakdownRaw = raw.breakdown;
  const timelineRaw = Array.isArray(raw.timeline) ? raw.timeline : [];

  return {
    ...base,
    title: str(raw.title, base.title),
    subtitle: str(raw.subtitle, base.subtitle),
    status,
    score: clamp(num(raw.score, base.score), 0, 100),
    percentile: clamp(num(raw.percentile, base.percentile), 0, 100),
    momentum_7d: clamp(num(raw.momentum_7d, base.momentum_7d), -100, 100),
    tier: str(raw.tier, base.tier),
    confidence: clamp(num(raw.confidence, base.confidence), 0, 1),

    why_now: Array.isArray(raw.why_now)
      ? raw.why_now.filter((x): x is string => typeof x === "string")
      : base.why_now,

    breakdown: {
      severity: clamp(getNum(breakdownRaw, "severity", base.breakdown.severity), 0, 100),
      recurrence: clamp(getNum(breakdownRaw, "recurrence", base.breakdown.recurrence), 0, 100),
      exploitability: clamp(getNum(breakdownRaw, "exploitability", base.breakdown.exploitability), 0, 100),
      competition: clamp(getNum(breakdownRaw, "competition", base.breakdown.competition), 0, 100),
      freshness: clamp(getNum(breakdownRaw, "freshness", base.breakdown.freshness), 0, 100),
    },

    timeline: timelineRaw
      .filter(isObj)
      .map((t) => ({
        label: str(t.label, "—"),
        at: str(t.at, "—"),
        kind:
          t.kind === "emerging" || t.kind === "breakout" || t.kind === "declining" || t.kind === "info"
            ? (t.kind as TimelinePoint["kind"])
            : "info",
      })),
  };
}

async function fetchClusterDetail(id: string): Promise<ClusterDetail> {
  const raw = await fetchJson<unknown>(`/clusters/${id}`);
  return normalizeClusterDetail(id, raw);
}

export function useClusterDetail(id: string) {
  return useQuery({
    queryKey: ["clusters", "detail", id],
    queryFn: () => fetchClusterDetail(id),
    enabled: !!id,
    staleTime: 30_000,
  });
}
