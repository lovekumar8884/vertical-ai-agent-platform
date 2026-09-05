import type { NextConfig } from "next";

// Standalone output is only needed for the container build (set in the
// Dockerfile). It uses symlinks that require elevated privileges on Windows,
// so keep it off for local `next build`.
const nextConfig: NextConfig = {
  reactStrictMode: true,
  ...(process.env.NEXT_STANDALONE === "1" ? { output: "standalone" as const } : {}),
};

export default nextConfig;
