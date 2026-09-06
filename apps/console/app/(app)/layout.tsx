import Link from "next/link";
import type { ReactNode } from "react";

// Authenticated app segment: rendered per-request (Clerk session required).
export const dynamic = "force-dynamic";

const NAV = [
  { href: "/agents", label: "Agents" },
  { href: "/conversations", label: "Conversations" },
  { href: "/settings/members", label: "Members" },
];

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-56 shrink-0 border-r bg-muted/30 p-4">
        <div className="mb-6 px-2 text-sm font-semibold">Vertical AI</div>
        <nav className="flex flex-col gap-1">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-md px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
