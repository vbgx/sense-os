"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Props {
  data: { name: string; value: number }[];
}

export function BarContributionChart({ data }: Props) {
  return (
    <div className="h-[240px] w-full">
      <ResponsiveContainer>
        <BarChart data={data}>
          <XAxis dataKey="name" hide />
          <YAxis hide />
          <Tooltip />
          <Bar dataKey="value" fill="currentColor" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
