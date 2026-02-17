"use client";

import Link from "next/link";
import type { TopPain } from "@/lib/api/schemas";

function Card({
  title,
  value,
  clusterId,
  subtitle,
}: {
  title: string;
  value: string;
  clusterId?: string;
  subtitle?: string;
}) {
  const body = (
    <div className="rounded-md border p-4 hover:bg-muted/40">
      <div className="text-xs text-muted-foreground">{title}</div>
      <div className="mt-1 text-lg font-semibold tabular-nums">{value}</div>
      {subtitle && <div className="mt-1 text-xs text-muted-foreground">{subtitle}</div>}
    </div>
  );

  return clusterId ? (
    <Link href={`/clusters/${encodeURIComponent(clusterId)}`} className="block">
      {body}
    </Link>
  ) : (
    body
  );
}

function mostCommon(items: string[]) {
  const m = new Map<string, number>();
  for (const s of items) m.set(s, (m.get(s) ?? 0) + 1);
  let best = "—";
  let bestN = 0;
  for (const [k, n] of m.entries()) {
    if (n > bestN) {
      best = k;
      bestN = n;
    }
  }
  return { value: best, count: bestN };
}

export function Highlights(props: {
  top: TopPain[];
  emerging: TopPain[];
  declining: TopPain[];
}) {
  const fastestBreakout =
    props.emerging.reduce<TopPain | null>(
      (acc, it) => (!acc || it.breakout_score > acc.breakout_score ? it : acc),
      null
    ) ?? null;

  const highestSeverity =
    props.top.reduce<TopPain | null>(
      (acc, it) => (!acc || it.severity_score > acc.severity_score ? it : acc),
      null
    ) ?? null;

  const highestConfidence =
    props.top.reduce<TopPain | null>(
      (acc, it) => (!acc || it.confidence_score > acc.confidence_score ? it : acc),
      null
    ) ?? null;

  const persona = mostCommon(props.top.map((x) => x.dominant_persona));

  return (
    <div className="space-y-2">
      <div className="text-sm font-medium">Highlights</div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Card
          title="Fastest breakout"
          value={fastestBreakout ? String(fastestBreakout.breakout_score) : "—"}
          clusterId={fastestBreakout?.cluster_id}
          subtitle={fastestBreakout?.cluster_summary ?? undefined}
        />
        <Card
          title="Highest severity"
          value={highestSeverity ? String(highestSeverity.severity_score) : "—"}
          clusterId={highestSeverity?.cluster_id}
          subtitle={highestSeverity?.cluster_summary ?? undefined}
        />
        <Card
          title="Highest confidence"
          value={highestConfidence ? String(highestConfidence.confidence_score) : "—"}
          clusterId={highestConfidence?.cluster_id}
          subtitle={highestConfidence?.cluster_summary ?? undefined}
        />
        <Card
          title="Dominant persona (top pains)"
          value={persona.value}
          subtitle={persona.value === "—" ? undefined : `${persona.count} clusters`}
        />
      </div>
    </div>
  );
}
