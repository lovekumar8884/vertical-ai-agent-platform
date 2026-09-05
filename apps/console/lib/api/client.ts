import type { HealthStatus, Problem, ReadyStatus } from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_VSA_API_BASE_URL ?? "http://localhost:8000";

/** Thrown for non-2xx responses; carries the Problem+JSON body when present. */
export class ApiError extends Error {
  readonly status: number;
  readonly problem: Problem | null;

  constructor(status: number, problem: Problem | null, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.problem = problem;
  }
}

export interface RequestOptions {
  method?: string;
  body?: unknown;
  signal?: AbortSignal;
  headers?: Record<string, string>;
}

export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, signal, headers = {} } = options;

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    signal,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...headers },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    let problem: Problem | null = null;
    try {
      problem = (await response.json()) as Problem;
    } catch {
      problem = null;
    }
    throw new ApiError(
      response.status,
      problem,
      problem?.detail ?? response.statusText,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

/** Typed endpoint methods. Extended as the API surface grows. */
export const api = {
  health: (signal?: AbortSignal) =>
    apiFetch<HealthStatus>("/healthz", { signal }),
  ready: (signal?: AbortSignal) => apiFetch<ReadyStatus>("/readyz", { signal }),
};
