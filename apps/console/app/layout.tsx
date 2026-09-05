import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vertical AI Agent Platform",
  description: "Console for building and testing AI Employees.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-neutral-900 antialiased">
        {children}
      </body>
    </html>
  );
}
