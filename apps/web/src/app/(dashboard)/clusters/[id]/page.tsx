
"use client";

import { useParams } from "next/navigation";
import { useClusterDetail } from "@/lib/api/queries";

export default function ClusterPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id ? String(params.id) : "";

  const q = useClusterDetail(id, Boolean(id));
  const data = q.data as any;

  const topPhrases: any[] = data?.top_phrases ?? data?.phrases ?? [];
  const topSignals: any[] = data?.top_signals ?? data?.signals ?? [];

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border bg-card/40 p-4">
        <div className="text-sm font-semibold">Cluster</div>
        <div className="mt-2 text-xs text-muted-foreground font-mono">id={id || "—"}</div>
      </div>

      <div className="rounded-2xl border bg-card/40 p-4">
        <div className="text-sm font-semibold">Top phrases</div>
        <div className="mt-2 space-y-1">
          {topPhrases.length === 0 ? (
            <div className="text-xs text-muted-foreground">—</div>
          ) : (
            topPhrases.map((p: any, idx: number) => (
              <div key={p?.id ?? idx} className="text-xs text-muted-foreground font-mono">
                {String(p?.text ?? p?.phrase ?? p?.value ?? "")}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="rounded-2xl border bg-card/40 p-4">
        <div className="text-sm font-semibold">Top signals</div>
        <div className="mt-2 space-y-1">
          {topSignals.length === 0 ? (
            <div className="text-xs text-muted-foreground">—</div>
          ) : (
            topSignals.map((s: any, idx: number) => (
              <div key={s?.id ?? idx} className="text-xs text-muted-foreground font-mono">
                {String(s?.text ?? s?.title ?? s?.value ?? "")}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
