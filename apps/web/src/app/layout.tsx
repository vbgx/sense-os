import "./globals.css";
import type { Metadata } from "next";
import { ThemeProvider } from "@/providers/ThemeProvider";
import { QueryProvider } from "@/providers/QueryProvider";
import { ToastProvider } from "@/providers/ToastProvider";
import { CommandPaletteContainer } from "@/components/layout/CommandPaletteContainer";

export const metadata: Metadata = {
  title: "Sense-OS",
  description: "Market Pain Intelligence Engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <QueryProvider>
            {children}
            <ToastProvider />
            <CommandPaletteContainer />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
