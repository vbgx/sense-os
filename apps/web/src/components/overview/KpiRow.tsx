"use client";

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}

export function KpiRow(props: {
  clustersSurfaced: number;
  emergingPct: number;
  decliningPct: number;
  avgExploitability: number;
}) {
  const pct = (v: number) => `${Math.round(v * 100)}%`;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <Stat label="Clusters surfaced" value={String(props.clustersSurfaced)} />
      <Stat label="% emerging (in surfaced)" value={pct(props.emergingPct)} />
      <Stat label="% declining (in surfaced)" value={pct(props.decliningPct)} />
      <Stat label="Avg exploitability" value={props.avgExploitability.toFixed(1)} />
    </div>
  );
}
