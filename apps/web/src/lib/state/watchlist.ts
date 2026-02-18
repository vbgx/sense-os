"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

const KEY = "sense.watchlist.v1";

type WatchlistState = {
  ids: Record<string, number>; // id -> added_at_ms
};

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null;
}

function loadInitial(): WatchlistState {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return { ids: {} };
    const parsed = JSON.parse(raw) as unknown;
    if (!isRecord(parsed)) return { ids: {} };

    const ids = (parsed as { ids?: unknown }).ids;
    if (!isRecord(ids)) return { ids: {} };

    const out: Record<string, number> = {};
    for (const [k, v] of Object.entries(ids)) {
      if (typeof k === "string" && typeof v === "number") out[k] = v;
    }
    return { ids: out };
  } catch {
    return { ids: {} };
  }
}

function persist(s: WatchlistState) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    // ignore
  }
}

export type WatchlistItem = { id: string; added_at: number };

export function useWatchlist() {
  const [state, setState] = useState<WatchlistState>(loadInitial);

  useEffect(() => {
    persist(state);
  }, [state]);

  const isStarred = useCallback((id: string) => Boolean(state.ids[id]), [state.ids]);

  const toggle = useCallback((id: string) => {
    setState((prev) => {
      const next: WatchlistState = { ids: { ...prev.ids } };
      if (next.ids[id]) delete next.ids[id];
      else next.ids[id] = Date.now();
      return next;
    });
  }, []);

  const remove = useCallback((id: string) => {
    setState((prev) => {
      if (!prev.ids[id]) return prev;
      const next: WatchlistState = { ids: { ...prev.ids } };
      delete next.ids[id];
      return next;
    });
  }, []);

  const items: WatchlistItem[] = useMemo(() => {
    return Object.entries(state.ids)
      .map(([id, added_at]) => ({ id, added_at }))
      .sort((a, b) => b.added_at - a.added_at);
  }, [state.ids]);

  return {
    items,
    count: items.length,
    isStarred,
    toggle,
    remove,
  };
}
