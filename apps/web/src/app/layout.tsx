import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "Sense",
  description: "Decision-first opportunity engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-white text-black">

        {/* Top Navigation */}
        <nav className="border-b px-6 py-4 flex gap-6 items-center">
          <Link href="/opportunity" className="font-semibold">
            Opportunities
          </Link>

          <Link href="/opportunity?emerging_only=true">
            Emerging
          </Link>

          <Link href="/builder">
            Builder Mode
          </Link>
        </nav>

        <main>{children}</main>

      </body>
    </html>
  );
}
