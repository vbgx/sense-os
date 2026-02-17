"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Command as CommandRoot } from "cmdk";

export type CommandItem = {
  id: string;
  label: string;
  hint?: string;
  href: string;
  keywords?: string[];
  kind: "page" | "cluster" | "vertical";
};

type Group = { heading: string; items: CommandItem[] };

type Props = {
  pages: CommandItem[];
  clusters: CommandItem[];
  verticals: CommandItem[];
};

function useCmdKToggle(onToggle: () => void) {
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const isK = e.key.toLowerCase() === "k";
      if ((e.metaKey || e.ctrlKey) && isK) {
        e.preventDefault();
        onToggle();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onToggle]);
}

export function CommandPalette({ pages, clusters, verticals }: Props) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState("");

  useCmdKToggle(() => {
    setOpen((v) => {
      const next = !v;
      if (!next) setValue("");
      return next;
    });
  });

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setOpen(false);
        setValue("");
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open]);

  const groups: Group[] = useMemo(() => {
    return [
      { heading: "Navigate", items: pages },
      { heading: "Verticals", items: verticals },
      { heading: "Clusters", items: clusters },
    ].filter((g) => g.items.length > 0);
  }, [pages, verticals, clusters]);

  const close = () => {
    setOpen(false);
    setValue("");
  };

  const onSelect = (href: string) => {
    close();
    router.push(href);
  };

  if (!open) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
        onClick={close}
      />

      <div className="fixed left-1/2 top-[18%] z-50 w-[720px] max-w-[92vw] -translate-x-1/2 rounded-2xl border bg-background shadow-2xl">
        <CommandRoot
          value={value}
          onValueChange={setValue}
          className="w-full"
          loop
        >
          <div className="border-b px-4 py-3">
            <CommandRoot.Input
              placeholder="Search clusters, verticals, pages…"
              className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
              autoFocus
            />
            <div className="mt-2 text-xs text-muted-foreground">
              Tip: <span className="font-medium">Cmd</span>+<span className="font-medium">K</span>
              {" · "}
              <span className="font-medium">Esc</span> to close
            </div>
          </div>

          <CommandRoot.List className="max-h-[420px] overflow-auto p-2">
            <CommandRoot.Empty className="p-4 text-sm text-muted-foreground">
              No results.
            </CommandRoot.Empty>

            {groups.map((group) => (
              <CommandRoot.Group key={group.heading} heading={group.heading}>
                {group.items.map((item) => (
                  <CommandRoot.Item
                    key={item.id}
                    value={[item.label, ...(item.keywords ?? [])].join(" ")}
                    onSelect={() => onSelect(item.href)}
                    className="flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-sm aria-selected:bg-muted"
                  >
                    <div className="min-w-0">
                      <div className="truncate">{item.label}</div>
                      {item.hint ? (
                        <div className="truncate text-xs text-muted-foreground">
                          {item.hint}
                        </div>
                      ) : null}
                    </div>

                    <div className="ml-3 text-xs text-muted-foreground">
                      {item.kind === "cluster"
                        ? "Cluster"
                        : item.kind === "vertical"
                          ? "Vertical"
                          : "Page"}
                    </div>
                  </CommandRoot.Item>
                ))}
              </CommandRoot.Group>
            ))}
          </CommandRoot.List>
        </CommandRoot>
      </div>
    </>
  );
}
