"use client";

import { useCallback, useMemo } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

export type DashboardQueryState = {
  q: string;
  vertical_id?: string;
  sort: string;
  limit: number;
  offset: number;
  inspect?: string;
  tier?: string;
  emerging_only?: boolean;
};

const DEFAULTS: DashboardQueryState = {
  q: "",
  sort: "score_desc",
  limit: 25,
  offset: 0,
};

function parseNumber(value: string | null, fallback: number): number {
  if (!value) return fallback;
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function parseBool(value: string | null): boolean | undefined {
  if (value === null) return undefined;
  if (value === "1" || value === "true") return true;
  if (value === "0" || value === "false") return false;
  return undefined;
}

export function useDashboardQueryState() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const state: DashboardQueryState = useMemo(() => {
    return {
      q: searchParams.get("q") ?? DEFAULTS.q,
      vertical_id: searchParams.get("vertical_id") ?? undefined,
      tier: searchParams.get("tier") ?? undefined,
      sort: searchParams.get("sort") ?? DEFAULTS.sort,
      limit: parseNumber(searchParams.get("limit"), DEFAULTS.limit),
      offset: parseNumber(searchParams.get("offset"), DEFAULTS.offset),
      inspect: searchParams.get("inspect") ?? undefined,
      emerging_only: parseBool(searchParams.get("emerging_only")),
    };
  }, [searchParams]);

  const update = useCallback(
    (patch: Partial<DashboardQueryState>) => {
      const params = new URLSearchParams(searchParams.toString());

      Object.entries(patch).forEach(([key, value]) => {
        const k = key as keyof DashboardQueryState;
        const isDefault = value === DEFAULTS[k] || value === undefined || value === "";

        if (isDefault) {
          params.delete(key);
        } else {
          params.set(key, String(value));
        }
      });

      router.push(`${pathname}?${params.toString()}`);
    },
    [router, pathname, searchParams]
  );

  const reset = useCallback(() => {
    router.push(pathname);
  }, [router, pathname]);

  return { state, update, reset };
}
