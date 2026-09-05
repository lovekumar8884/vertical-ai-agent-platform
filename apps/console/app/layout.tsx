import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vertical AI Agent Platform",
  description: "Console for building and testing AI Employees.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const document = (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );

  // Wrap with Clerk only when configured, so the app still builds/renders
  // without keys (auth routes are dynamic and simply require keys at runtime).
  if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    return document;
  }
  return <ClerkProvider>{document}</ClerkProvider>;
}
