/** Shared API types. Expanded per resource as endpoints land (generated from
 * the OpenAPI spec in a later sprint). */

/** RFC 7807 Problem+JSON, as returned by the API's error handlers. */
export interface Problem {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  code?: string;
}

export interface HealthStatus {
  status: string;
}

export interface ReadyStatus {
  status: "ready" | "not_ready";
  checks: Record<string, string>;
}
