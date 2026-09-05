import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/**
 * Baseline security headers on every response. Clerk auth is wired in a later
 * commit; this establishes HSTS + hardening headers first.
 */
export function middleware(_request: NextRequest) {
  const response = NextResponse.next();
  response.headers.set(
    "Strict-Transport-Security",
    "max-age=63072000; includeSubDomains; preload",
  );
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
