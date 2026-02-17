"use client";

import Link from "next/link";
import type { Vertical } from "@/lib/api/schemas";

export function VerticalTable({ items }: { items: Vertical[] }) {
  return (
    <div className="rounded-md border" data-testid="vertical-table">
      <div className="border-b px-4 py-3">
        <div className="text-sm font-medium">Verticals</div>
        <div className="text-xs text-muted-foreground">Ranking (v0): list provided by /verticals/</div>
      </div>

      <div className="grid grid-cols-12 gap-2 border-b bg-background px-4 py-2 text-xs font-medium text-muted-foreground">
        <div className="col-span-2">ID</div>
        <div className="col-span-8">Name</div>
        <div className="col-span-2">Open</div>
      </div>

      <div className="divide-y">
        {items.map((v) => (
          <div
            key={v.id}
            className="grid grid-cols-12 gap-2 px-4 py-3 hover:bg-muted/40"
            data-testid="vertical-row"
            data-vertical-id={v.id}
          >
            <div className="col-span-2 text-sm tabular-nums">{v.id}</div>
            <div className="col-span-8 text-sm font-medium">{v.name}</div>
            <div className="col-span-2">
              <Link
                className="text-sm underline underline-offset-2"
                href={`/verticals/${encodeURIComponent(String(v.id))}`}
              >
                Open
              </Link>
            </div>
          </div>
        ))}

        {items.length === 0 && (
          <div className="px-4 py-6 text-sm text-muted-foreground">No verticals.</div>
        )}
      </div>
    </div>
  );
}
