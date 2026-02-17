"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

const KEY = "sense.portfolio.v1";

type PortfolioState = {
  tracked: Record<string, number>; // cluster_id -> ts
};

function safeParse(raw: string | null): PortfolioState {
  if (!raw) return { tracked: {} };
  try {
    const x = JSON.parse(raw) as unknown;
    if (typeof x !== "object" || x === null) return { tracked: {} };
    const tracked = (x as { tracked?: unknown }).tracked;
    if (typeof tracked !== "object" || tracked === null) return { tracked: {} };

    const rec: Record<string, number> = {};
    for (const [k, v] of Object.entries(tracked as Record<string, unknown>)) {
      if (typeof k === "string" && typeof v === "number") rec[k] = v;
    }
    return { tracked: rec };
  } catch {
    return { tracked: {} };
  }
}

function loadInitial(): PortfolioState {
  // "use client" => safe to access window during initialization in Next app router client component
  try {
    return safeParse(window.localStorage.getItem(KEY));
  } catch {
    return { tracked: {} };
  }
}

function save(s: PortfolioState) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    // ignore quota / private mode
  }
}

export type PortfolioItem = { cluster_id: string; added_at: number };

export function usePortfolio() {
  const [state, setState] = useState<PortfolioState>(loadInitial);

  // Persist on change (external system write is OK in an effect)
  useEffect(() => {
    save(state);
  }, [state]);

  const isTracked = useCallback((clusterId: string) => Boolean(state.tracked[clusterId]), [state.tracked]);

  const toggle = useCallback((clusterId: string) => {
    setState((prev) => {
      const next = { tracked: { ...prev.tracked } };
      if (next.tracked[clusterId]) delete next.tracked[clusterId];
      else next.tracked[clusterId] = Date.now();
      return next;
    });
  }, []);

  const add = useCallback((clusterId: string) => {
    setState((prev) => {
      if (prev.tracked[clusterId]) return prev;
      return { tracked: { ...prev.tracked, [clusterId]: Date.now() } };
    });
  }, []);

  const remove = useCallback((clusterId: string) => {
    setState((prev) => {
      if (!prev.tracked[clusterId]) return prev;
      const next = { tracked: { ...prev.tracked } };
      delete next.tracked[clusterId];
      return next;
    });
  }, []);

  const items: PortfolioItem[] = useMemo(() => {
    return Object.entries(state.tracked)
      .map(([cluster_id, added_at]) => ({ cluster_id, added_at }))
      .sort((a, b) => b.added_at - a.added_at);
  }, [state.tracked]);

  const count = items.length;

  return { items, count, isTracked, toggle, add, remove };
}
