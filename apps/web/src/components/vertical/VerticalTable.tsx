"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Vertical } from "@/lib/api/schemas";

type FilterValue = "all" | string;

export function VerticalTable({ items }: { items: Vertical[] }) {
  const [industryFilter, setIndustryFilter] = useState<FilterValue>("all");
  const [functionFilter, setFunctionFilter] = useState<FilterValue>("all");
  const [tierFilter, setTierFilter] = useState<FilterValue>("all");

  const options = useMemo(() => {
    const industries = new Set<string>();
    const functions = new Set<string>();
    const tiers = new Set<string>();

    items.forEach((v) => {
      if (v.meta?.industry) industries.add(String(v.meta.industry));
      if (v.meta?.function) functions.add(String(v.meta.function));
      if (v.tier) tiers.add(String(v.tier));
    });

    return {
      industries: Array.from(industries).sort(),
      functions: Array.from(functions).sort(),
      tiers: Array.from(tiers).sort(),
    };
  }, [items]);

  const filteredItems = useMemo(() => {
    return items.filter((v) => {
      if (industryFilter !== "all" && v.meta?.industry !== industryFilter) return false;
      if (functionFilter !== "all" && v.meta?.function !== functionFilter) return false;
      if (tierFilter !== "all" && v.tier !== tierFilter) return false;
      return true;
    });
  }, [items, industryFilter, functionFilter, tierFilter]);

  return (
    <div className="rounded-md border" data-testid="vertical-table">
      <div className="border-b px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-sm font-medium">Verticals</div>
            <div className="text-xs text-muted-foreground">
              Ranking (v0): list provided by /verticals/ • {filteredItems.length} shown
            </div>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <label className="flex items-center gap-2">
              <span className="text-muted-foreground">Industry</span>
              <select
                className="h-7 rounded-md border bg-background px-2 text-xs"
                value={industryFilter}
                onChange={(event) => setIndustryFilter(event.target.value)}
              >
                <option value="all">All</option>
                {options.industries.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-2">
              <span className="text-muted-foreground">Function</span>
              <select
                className="h-7 rounded-md border bg-background px-2 text-xs"
                value={functionFilter}
                onChange={(event) => setFunctionFilter(event.target.value)}
              >
                <option value="all">All</option>
                {options.functions.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-2">
              <span className="text-muted-foreground">Tier</span>
              <select
                className="h-7 rounded-md border bg-background px-2 text-xs"
                value={tierFilter}
                onChange={(event) => setTierFilter(event.target.value)}
              >
                <option value="all">All</option>
                {options.tiers.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-2 border-b bg-background px-4 py-2 text-xs font-medium text-muted-foreground">
        <div className="col-span-2">ID</div>
        <div className="col-span-4">Name</div>
        <div className="col-span-2">Industry</div>
        <div className="col-span-2">Function</div>
        <div className="col-span-1">Tier</div>
        <div className="col-span-1">Open</div>
      </div>

      <div className="divide-y">
        {filteredItems.map((v) => (
          <div
            key={v.id}
            className="grid grid-cols-12 gap-2 px-4 py-3 hover:bg-muted/40"
            data-testid="vertical-row"
            data-vertical-id={v.id}
          >
            <div className="col-span-2 text-sm tabular-nums">{v.id}</div>
            <div className="col-span-4 text-sm font-medium">{v.name}</div>
            <div className="col-span-2 text-sm text-muted-foreground">
              {v.meta?.industry ?? "—"}
            </div>
            <div className="col-span-2 text-sm text-muted-foreground">
              {v.meta?.function ?? "—"}
            </div>
            <div className="col-span-1 text-sm text-muted-foreground">{v.tier ?? "—"}</div>
            <div className="col-span-1">
              <Link
                className="text-sm underline underline-offset-2"
                href={`/verticals/${encodeURIComponent(String(v.id))}`}
              >
                Open
              </Link>
            </div>
          </div>
        ))}

        {filteredItems.length === 0 && (
          <div className="px-4 py-6 text-sm text-muted-foreground">No verticals.</div>
        )}
      </div>
    </div>
  );
}
