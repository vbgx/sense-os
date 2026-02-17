"use client";

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useRef } from "react";
import type { TopPain } from "@/lib/api/schemas";

interface Props {
  data: TopPain[];
  onRowClick?: (clusterId: string) => void;
}

export function OpportunityTable({ data, onRowClick }: Props) {
  const columns: ColumnDef<TopPain>[] = [
    { header: "Summary", accessorKey: "cluster_summary" },
    { header: "Exploitability", accessorKey: "exploitability_score" },
    { header: "Growth", accessorKey: "breakout_score" },
    { header: "Severity", accessorKey: "severity_score" },
    { header: "Underserved", accessorKey: "opportunity_window_status" },
    { header: "Confidence", accessorKey: "confidence_score" },
    { header: "Persona", accessorKey: "dominant_persona" },
  ];

  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 44,
    overscan: 10,
  });

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto rounded-md border">
      <table className="w-full text-sm">
        <thead className="sticky top-0 border-b bg-background">
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => (
                <th key={header.id} className="px-3 py-2 text-left font-medium">
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>

        <tbody>
          <tr>
            <td colSpan={columns.length}>
              <div style={{ height: rowVirtualizer.getTotalSize(), position: "relative" }}>
                {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                  const row = table.getRowModel().rows[virtualRow.index];

                  return (
                    <div
                      key={row.id}
                      role="button"
                      tabIndex={0}
                      className="absolute left-0 right-0 flex border-b hover:bg-muted/40 cursor-pointer"
                      style={{ transform: `translateY(${virtualRow.start}px)` }}
                      onClick={() => onRowClick?.(row.original.cluster_id)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") onRowClick?.(row.original.cluster_id);
                      }}
                    >
                      {row.getVisibleCells().map((cell) => {
                        const renderer = cell.column.columnDef.cell;
                        const value = cell.getValue();

                        return (
                          <div key={cell.id} className="flex-1 truncate px-3 py-2">
                            {renderer
                              ? flexRender(renderer, cell.getContext())
                              : value == null
                                ? "—"
                                : String(value)}
                          </div>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
