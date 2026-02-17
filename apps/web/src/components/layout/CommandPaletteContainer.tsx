"use client";

import { useMemo } from "react";
import { CommandPalette, type CommandItem } from "@/components/layout/CommandPalette";
import { useTopPains, useVerticals } from "@/lib/api/queries";

export function CommandPaletteContainer() {
  const top = useTopPains({ limit: 50, offset: 0 });
  const verticalsQ = useVerticals();

  const pages: CommandItem[] = useMemo(
    () => [
      { id: "page-overview", label: "Overview", href: "/overview", kind: "page" },
      { id: "page-opportunities", label: "Opportunities", href: "/opportunities", kind: "page" },
      { id: "page-emerging", label: "Emerging", href: "/emerging", kind: "page" },
      { id: "page-declining", label: "Declining", href: "/declining", kind: "page" },
      { id: "page-verticals", label: "Verticals", href: "/verticals", kind: "page" },
      { id: "page-analytics", label: "Analytics", href: "/analytics", kind: "page" },
    ],
    [],
  );

  const clusters: CommandItem[] = useMemo(() => {
    const data = top.data ?? [];
    return data
      .filter((c) => c && c.cluster_id)
      .slice(0, 50)
      .map((c) => ({
        id: `cluster-${c.cluster_id}`,
        label: c.cluster_summary?.trim() ? c.cluster_summary : `Cluster ${c.cluster_id}`,
        hint: [
          typeof c.exploitability_score === "number" ? `Exploitability ${c.exploitability_score}` : null,
          c.dominant_persona ? String(c.dominant_persona) : null,
        ]
          .filter(Boolean)
          .join(" · "),
        href: `/clusters/${encodeURIComponent(c.cluster_id)}`,
        keywords: [
          c.cluster_id,
          c.cluster_summary ?? "",
          c.dominant_persona ?? "",
          c.opportunity_window_status ?? "",
        ].filter(Boolean) as string[],
        kind: "cluster",
      }));
  }, [top.data]);

  const verticals: CommandItem[] = useMemo(() => {
    const vs = verticalsQ.data ?? [];
    return vs.map((v) => ({
      id: `vertical-${v.id}`,
      label: v.name,
      hint: v.description ? String(v.description) : undefined,
      href: `/verticals/${encodeURIComponent(String(v.id))}`,
      keywords: [v.name].filter(Boolean),
      kind: "vertical",
    }));
  }, [verticalsQ.data]);

  return <CommandPalette pages={pages} clusters={clusters} verticals={verticals} />;
}
