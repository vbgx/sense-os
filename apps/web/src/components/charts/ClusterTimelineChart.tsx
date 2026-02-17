"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import type { TimelinePoint } from "@/lib/api/schemas";

export function ClusterTimelineChart({ data }: { data: TimelinePoint[] }) {
  return (
    <div className="h-[240px] w-full" data-testid="timeline-chart">
      <ResponsiveContainer>
        <LineChart data={data}>
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="volume" dot={false} />
          <Line type="monotone" dataKey="velocity" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
