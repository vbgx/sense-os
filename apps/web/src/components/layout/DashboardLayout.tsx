"use client";

import { ReactNode } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen grid grid-cols-[260px_1fr]">
      <Sidebar />
      <main className="px-6 py-7">
        <Topbar />
        <div className="mt-5">{children}</div>
      </main>
    </div>
  );
}
