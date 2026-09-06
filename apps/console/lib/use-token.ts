"use client";

import { useAuth } from "@clerk/nextjs";

/** Returns a getter for the Clerk session JWT used to authenticate API calls. */
export function useToken() {
  const { getToken } = useAuth();
  return getToken;
}
