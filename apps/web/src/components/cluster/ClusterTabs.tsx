"use client";

import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";

export type ClusterTabKey = "signals" | "wedge" | "validation" | "timeline";

type Tab = {
  key: ClusterTabKey;
  label: string;
  hint: string;
};

const TABS: Tab[] = [
  { key: "signals", label: "Signals", hint: "Representative examples + volume cues" },
  { key: "wedge", label: "Wedge", hint: "How we win + product angle" },
  { key: "validation", label: "Validation", hint: "Fast tests + stop condition" },
  { key: "timeline", label: "Timeline", hint: "Emerging → Breakout → Declining markers" },
];

type Props = {
  initial?: ClusterTabKey;
  clusterId: string;
  className?: string;
};

function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <section className="sense-panel rounded-2xl border">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
        <div className="flex flex-col gap-0.5">
          <div className="text-sm font-semibold tracking-tight">{title}</div>
          <div className="text-xs text-muted-foreground">{subtitle}</div>
        </div>
        <div className="font-mono text-[11px] text-muted-foreground">mock · v0</div>
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}

export function ClusterTabs({ initial = "signals", clusterId, className }: Props) {
  const [active, setActive] = useState<ClusterTabKey>(initial);

  const activeMeta = useMemo(() => TABS.find((t) => t.key === active)!, [active]);

  return (
    <div className={cn("space-y-3", className)}>
      {/* Tabs bar */}
      <div className="sense-panel rounded-2xl border px-3 py-2">
        <div className="flex flex-wrap items-center gap-2">
          {TABS.map((t) => {
            const on = t.key === active;
            return (
              <button
                key={t.key}
                type="button"
                onClick={() => setActive(t.key)}
                className={cn(
                  "rounded-xl border px-3 py-2 text-sm transition",
                  on
                    ? "border-white/15 bg-white/5 text-white/90"
                    : "border-transparent text-muted-foreground hover:border-white/10 hover:bg-white/5 hover:text-white/85"
                )}
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">{t.label}</span>
                  <span className="hidden font-mono text-[11px] text-muted-foreground/70 md:inline">
                    {t.key}
                  </span>
                </div>
              </button>
            );
          })}
          <div className="ml-auto hidden items-center gap-2 md:flex">
            <span className="font-mono text-[11px] text-muted-foreground/70">cluster_id</span>
            <span className="rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
              {clusterId}
            </span>
          </div>
        </div>

        <div className="mt-2 border-t border-white/10 pt-2 text-xs text-muted-foreground">
          <span className="font-semibold text-white/80">{activeMeta.label}:</span> {activeMeta.hint}
        </div>
      </div>

      {/* Tab content */}
      {active === "signals" ? (
        <Panel title="Signals" subtitle="Examples that prove recurrence + persona specificity">
          <div className="grid gap-3 md:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="sense-card rounded-2xl border p-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="text-xs text-muted-foreground">source=reddit · confidence=0.83</div>
                  <div className="rounded-full border border-white/10 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                    score +{(12 - i).toFixed(0)}
                  </div>
                </div>
                <div className="mt-2 text-sm text-white/90">
                  “We waste hours coordinating evidence and approvals across tools before every audit…”
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-muted-foreground">
                  <span className="rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono">persona=ops</span>
                  <span className="rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono">theme=compliance</span>
                  <span className="rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono">recurrence=high</span>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      ) : null}

      {active === "wedge" ? (
        <Panel title="Wedge" subtitle="How we win quickly without boiling the ocean">
          <div className="grid gap-3 lg:grid-cols-3">
            <div className="sense-card rounded-2xl border p-3">
              <div className="text-xs text-muted-foreground">Wedge</div>
              <div className="mt-2 text-sm font-semibold text-white/90">Evidence hub + workflow handoffs</div>
              <div className="mt-2 text-xs text-muted-foreground">
                Centralize audit evidence, owners, and handoffs. Reduce coordination overhead first.
              </div>
            </div>
            <div className="sense-card rounded-2xl border p-3">
              <div className="text-xs text-muted-foreground">Monetization</div>
              <div className="mt-2 text-sm font-semibold text-white/90">Per-workspace + compliance seats</div>
              <div className="mt-2 text-xs text-muted-foreground">
                Land with ops → expand to security/QA. Pricing aligned with audit cycle urgency.
              </div>
            </div>
            <div className="sense-card rounded-2xl border p-3">
              <div className="text-xs text-muted-foreground">Moat</div>
              <div className="mt-2 text-sm font-semibold text-white/90">Workflow data → scoring + playbooks</div>
              <div className="mt-2 text-xs text-muted-foreground">
                Once installed, you own the evidence graph and execution rituals.
              </div>
            </div>
          </div>
        </Panel>
      ) : null}

      {active === "validation" ? (
        <Panel title="Validation" subtitle="6-week tests + stop condition to prevent delusion">
          <div className="space-y-3">
            {[
              { k: "Test #1", v: "10 interviews with ops managers, measure time lost per audit cycle" },
              { k: "Test #2", v: "Prototype evidence checklist + owner handoff → observe adoption in 48h" },
              { k: "Test #3", v: "Landing page w/ “audit evidence hub” + run ads to ops keywords" },
              { k: "Stop", v: "If no repeatable ‘coordination overhead’ language in 8/10 calls → kill" },
            ].map((x) => (
              <div key={x.k} className="sense-card rounded-2xl border p-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="font-mono text-[11px] text-muted-foreground">{x.k}</div>
                  <span className="rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                    v1
                  </span>
                </div>
                <div className="mt-2 text-sm text-white/90">{x.v}</div>
              </div>
            ))}
          </div>
        </Panel>
      ) : null}

      {active === "timeline" ? (
        <Panel title="Timeline" subtitle="Narrative markers that explain momentum">
          <div className="grid gap-3 md:grid-cols-2">
            <div className="sense-card rounded-2xl border p-3">
              <div className="text-xs text-muted-foreground">Last 90 days</div>
              <div className="mt-2 text-sm font-semibold text-white/90">Emerging → Breakout</div>
              <div className="mt-2 text-xs text-muted-foreground">
                Recurrence up · Confidence stable · Competition low → window open.
              </div>
            </div>
            <div className="sense-card rounded-2xl border p-3">
              <div className="text-xs text-muted-foreground">Markers</div>
              <div className="mt-2 flex flex-wrap gap-2">
                <span className="rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                  🌱 Emerging
                </span>
                <span className="rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                  🔥 Breakout
                </span>
                <span className="rounded-full border border-white/10 bg-black/20 px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                  ❄ Declining
                </span>
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                (Charts later) — for now we keep the decision narrative.
              </div>
            </div>
          </div>
        </Panel>
      ) : null}
    </div>
  );
}
