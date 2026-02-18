"use client";

import { useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { EmptyBlock } from "@/components/ui/EmptyBlock";
import { OverviewHeader } from "@/components/overview-v2/OverviewHeader";
import { qk } from "@/lib/api/queries";

type ExportStatus = "delivered" | "running" | "failed";
type SourceType = "vertical" | "cluster";
type Destination = "ventureos_api" | "download_json" | "copy_clipboard";
type TemplateKind = "ventureos_export_payload_v1" | "bet_slip_preview_v1" | "strategy_memo_v1";

type ExportRow = {
  id: string;
  source_type: SourceType;
  source_label: string;
  source_id: string;
  template: TemplateKind;
  status: ExportStatus;
  created_label: string; // mock like "9m" "1h"
};

type ExportSpec = {
  kind: TemplateKind;
  source: { type: SourceType; id: string };
  versions: { taxonomy_version: string; scoring_version: string };
  notes?: string | null;
  payload: {
    vertical_label?: string;
    cluster_label?: string;
    status?: string;
    score?: number;
    percentile?: number;
    momentum_7d?: number;
    confidence?: number;
    bet_slip?: {
      pain_statement: string;
      target_persona: string;
      suggested_wedge: string;
      monetization_angle: string;
      risk_flags: string[];
      early_validation_steps: string[];
    };
  };
};

const MOCK_HISTORY: ExportRow[] = [
  {
    id: "ex_001",
    source_type: "vertical",
    source_label: "Vertical: B2B Ops → Healthcare",
    source_id: "v_b2b_ops_healthcare",
    template: "ventureos_export_payload_v1",
    status: "delivered",
    created_label: "9m",
  },
  {
    id: "ex_002",
    source_type: "cluster",
    source_label: "Cluster: Compliance overhead",
    source_id: "cl_102",
    template: "bet_slip_preview_v1",
    status: "running",
    created_label: "14m",
  },
  {
    id: "ex_003",
    source_type: "vertical",
    source_label: "Vertical: Marketing → SEO Ops",
    source_id: "v_marketing_seo_ops",
    template: "strategy_memo_v1",
    status: "failed",
    created_label: "1h",
  },
];

function badgeFor(status: ExportStatus) {
  if (status === "delivered") return { text: "✅ delivered", cls: "border-emerald-500/30 bg-emerald-500/10 text-emerald-200" };
  if (status === "running") return { text: "⏳ running", cls: "border-amber-500/30 bg-amber-500/10 text-amber-200" };
  return { text: "❌ failed", cls: "border-rose-500/30 bg-rose-500/10 text-rose-200" };
}

function clampText(s: string, max = 220) {
  const t = s.trim();
  return t.length > max ? `${t.slice(0, max)}…` : t;
}

export default function Page() {
  const qc = useQueryClient();

  // Form state (mock)
  const [sourceType, setSourceType] = useState<SourceType>("vertical");
  const [sourceId, setSourceId] = useState<string>("v_b2b_ops_healthcare");
  const [template, setTemplate] = useState<TemplateKind>("ventureos_export_payload_v1");
  const [destination, setDestination] = useState<Destination>("ventureos_api");
  const [taxonomyVersion, setTaxonomyVersion] = useState<string>("2026-02-17");
  const [scoringVersion, setScoringVersion] = useState<string>("v2.0");
  const [notes, setNotes] = useState<string>("");

  // Mock updated label
  const updatedLabel = useMemo(() => "Updated —", []);

  const preview: ExportSpec = useMemo(() => {
    const isVertical = sourceType === "vertical";
    const safeId = sourceId.trim() || (isVertical ? "v_unknown" : "cl_unknown");

    const base: ExportSpec = {
      kind: template,
      source: { type: sourceType, id: safeId },
      versions: { taxonomy_version: taxonomyVersion.trim() || "—", scoring_version: scoringVersion.trim() || "—" },
      notes: notes.trim() ? clampText(notes.trim(), 260) : null,
      payload: {},
    };

    // Keep preview "nice" even in mock mode
    if (isVertical) {
      base.payload.vertical_label = "B2B Ops → Healthcare";
      base.payload.status = "HOT";
      base.payload.score = 81;
      base.payload.percentile = 0.94;
      base.payload.momentum_7d = 0.18;
      base.payload.confidence = 0.83;

      if (template !== "strategy_memo_v1") {
        base.payload.bet_slip = {
          pain_statement: "Compliance coordination overhead slows audits and execution.",
          target_persona: "Ops manager",
          suggested_wedge: "Evidence collection + workflow ownership + reminders",
          monetization_angle: "Per-seat + audit packs",
          risk_flags: ["Regulated workflows", "Procurement friction"],
          early_validation_steps: ["10 interviews", "concierge MVP", "pricing test"],
        };
      }
    } else {
      base.payload.cluster_label = "Compliance overhead";
      base.payload.status = "BREAKOUT";
      base.payload.score = 4.2;
      base.payload.confidence = 0.83;
      base.payload.bet_slip = {
        pain_statement: "Teams lose hours syncing compliance evidence across tools and stakeholders.",
        target_persona: "Ops lead",
        suggested_wedge: "Single evidence inbox + ownership routing",
        monetization_angle: "Team plans + compliance add-ons",
        risk_flags: ["Integration surface", "Audit requirements"],
        early_validation_steps: ["10 interviews", "data room prototype", "pilot with 2 teams"],
      };
    }

    return base;
  }, [destination, notes, scoringVersion, sourceId, sourceType, taxonomyVersion, template]);

  const history = MOCK_HISTORY; // later: from API

  return (
    <div className="space-y-6">
      <OverviewHeader
        updatedLabel={updatedLabel}
        onRefresh={() => {
          // keep consistent with the rest of cockpit: invalidate a "meta" key (safe no-op if missing)
          qc.invalidateQueries({ queryKey: qk.meta?.status?.() ?? ["meta", "status"] });
        }}
        isRefreshing={false}
      />

      <div className="rounded-2xl border bg-card/40">
        <div className="flex flex-wrap items-start justify-between gap-3 border-b px-4 py-3">
          <div>
            <div className="text-sm font-semibold">Export Center</div>
            <div className="mt-1 text-xs text-muted-foreground">
              Left: export history. Right: create a new export.
            </div>
          </div>
        </div>

        <div className="grid gap-3 p-4 lg:grid-cols-[1fr_420px]">
          {/* LEFT: HISTORY */}
          <div className="rounded-2xl border bg-background/20 p-3">
            <div className="text-sm font-semibold">Export History</div>
            <div className="mt-1 text-xs text-muted-foreground">
              Recent exports with status. Click a row later to view the exact payload that was generated.
            </div>

            {history.length === 0 ? (
              <div className="mt-3">
                <EmptyBlock
                  title="No exports yet"
                  description="Create your first deterministic export to VentureOS."
                  onAction={() => {
                    // focus first field later; for now just a stub
                    setSourceId((v) => v);
                  }}
                />
              </div>
            ) : (
              <div className="mt-3 overflow-hidden rounded-2xl border">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b">
                      <th className="px-3 py-2 text-left font-mono text-[11px] text-muted-foreground">Source</th>
                      <th className="px-3 py-2 text-left font-mono text-[11px] text-muted-foreground">Template</th>
                      <th className="px-3 py-2 text-left font-mono text-[11px] text-muted-foreground">Status</th>
                      <th className="px-3 py-2 text-right font-mono text-[11px] text-muted-foreground">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((r) => {
                      const b = badgeFor(r.status);
                      return (
                        <tr key={r.id} className="border-b last:border-b-0 hover:bg-white/5">
                          <td className="px-3 py-2 align-top">
                            <div className="flex flex-col gap-0.5">
                              <div className="text-sm font-medium">{r.source_label}</div>
                              <div className="font-mono text-[11px] text-muted-foreground">{r.source_id}</div>
                            </div>
                          </td>
                          <td className="px-3 py-2 align-top font-mono text-[12px] text-muted-foreground">
                            {r.template}
                          </td>
                          <td className="px-3 py-2 align-top">
                            <span className={`inline-flex items-center rounded-full border px-2 py-0.5 font-mono text-[11px] ${b.cls}`}>
                              {b.text}
                            </span>
                          </td>
                          <td className="px-3 py-2 align-top text-right font-mono text-[12px] text-muted-foreground">
                            {r.created_label}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}

            <div className="mt-3 text-xs text-muted-foreground">
              <span className="font-semibold text-foreground/80">Determinism:</span>{" "}
              payloads include taxonomy_version + scoring_version so you can reproduce exactly later.
            </div>
          </div>

          {/* RIGHT: CREATE EXPORT */}
          <div className="rounded-2xl border bg-background/20 p-3">
            <div className="text-sm font-semibold">Create Export</div>
            <div className="mt-1 text-xs text-muted-foreground">
              Generate a payload for VentureOS. This is the UI mock of the “Export window”.
            </div>

            <div className="mt-3 grid gap-3">
              <div className="grid gap-1.5">
                <div className="font-mono text-[11px] text-muted-foreground">Source type</div>
                <select
                  className="w-full rounded-2xl border bg-background/30 px-3 py-2 font-mono text-[12px]"
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value === "cluster" ? "cluster" : "vertical")}
                >
                  <option value="vertical">vertical</option>
                  <option value="cluster">cluster</option>
                </select>
                <div className="text-[11px] text-muted-foreground">
                  Vertical exports create a full “bet slip candidate”. Cluster exports create a focused pain memo.
                </div>
              </div>

              <div className="grid gap-1.5">
                <div className="font-mono text-[11px] text-muted-foreground">Source ID</div>
                <input
                  className="w-full rounded-2xl border bg-background/30 px-3 py-2 font-mono text-[12px]"
                  value={sourceId}
                  onChange={(e) => setSourceId(e.target.value)}
                />
                <div className="text-[11px] text-muted-foreground">
                  Example: <span className="font-mono">v_b2b_ops_healthcare</span> or <span className="font-mono">cl_102</span>
                </div>
              </div>

              <div className="grid gap-3 lg:grid-cols-2">
                <div className="grid gap-1.5">
                  <div className="font-mono text-[11px] text-muted-foreground">Template</div>
                  <select
                    className="w-full rounded-2xl border bg-background/30 px-3 py-2 font-mono text-[12px]"
                    value={template}
                    onChange={(e) => setTemplate(e.target.value as TemplateKind)}
                  >
                    <option value="ventureos_export_payload_v1">ventureos_export_payload_v1</option>
                    <option value="bet_slip_preview_v1">bet_slip_preview_v1</option>
                    <option value="strategy_memo_v1">strategy_memo_v1</option>
                  </select>
                  <div className="text-[11px] text-muted-foreground">
                    Templates map to your specs in <span className="font-mono">docs/specs/</span>.
                  </div>
                </div>

                <div className="grid gap-1.5">
                  <div className="font-mono text-[11px] text-muted-foreground">Destination</div>
                  <select
                    className="w-full rounded-2xl border bg-background/30 px-3 py-2 font-mono text-[12px]"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value as Destination)}
                  >
                    <option value="ventureos_api">VentureOS (API)</option>
                    <option value="download_json">Download JSON</option>
                    <option value="copy_clipboard">Copy to clipboard</option>
                  </select>
                  <div className="text-[11px] text-muted-foreground">Even “download” stays versioned.</div>
                </div>
              </div>

              <div className="grid gap-3 lg:grid-cols-2">
                <div className="grid gap-1.5">
                  <div className="font-mono text-[11px] text-muted-foreground">taxonomy_version</div>
                  <input
                    className="w-full rounded-2xl border bg-background/30 px-3 py-2 font-mono text-[12px]"
                    value={taxonomyVersion}
                    onChange={(e) => setTaxonomyVersion(e.target.value)}
                  />
                  <div className="text-[11px] text-muted-foreground">Frozen taxonomy snapshot version.</div>
                </div>

                <div className="grid gap-1.5">
                  <div className="font-mono text-[11px] text-muted-foreground">scoring_version</div>
                  <input
                    className="w-full rounded-2xl border bg-background/30 px-3 py-2 font-mono text-[12px]"
                    value={scoringVersion}
                    onChange={(e) => setScoringVersion(e.target.value)}
                  />
                  <div className="text-[11px] text-muted-foreground">Used to reproduce ranking.</div>
                </div>
              </div>

              <div className="grid gap-1.5">
                <div className="font-mono text-[11px] text-muted-foreground">Notes (optional)</div>
                <input
                  className="w-full rounded-2xl border bg-background/30 px-3 py-2 font-mono text-[12px]"
                  placeholder="e.g., If stays HOT 14d → commit to interviews"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              <button
                type="button"
                className="w-full rounded-2xl border border-orange-500/40 bg-orange-500/15 px-3 py-2 font-mono text-[12px] text-orange-100 hover:bg-orange-500/20"
                onClick={() => {
                  // mock “export”: later will enqueue job and push to history
                }}
              >
                ⤴ Export to VentureOS
              </button>

              <button
                type="button"
                className="w-full rounded-2xl border bg-background/30 px-3 py-2 font-mono text-[12px] hover:bg-white/5"
                onClick={() => {
                  // noop: preview already shown
                }}
              >
                Preview payload
              </button>

              <div className="rounded-2xl border bg-black/20 p-3 font-mono text-[11px] leading-relaxed text-white/80">
                {JSON.stringify(preview, null, 2)}
              </div>

              <div className="text-[11px] text-muted-foreground">
                <span className="font-semibold text-foreground/80">UX rule:</span> exporting should be 1 click, but preview must always show the exact deterministic JSON.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
