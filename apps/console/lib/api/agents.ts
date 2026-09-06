import { apiFetch } from "./client";
import type { Agent, AgentCreate } from "./types";

export function listAgents(token: string | null) {
  return apiFetch<Agent[]>("/v1/agents", { token });
}

export function createAgent(token: string | null, body: AgentCreate) {
  return apiFetch<Agent>("/v1/agents", {
    method: "POST",
    body,
    token,
    headers: { "Idempotency-Key": crypto.randomUUID() },
  });
}
