import { apiFetch } from "./client";
import type { Member, MeResponse, Session, Turn } from "./types";

export function getMe(token: string | null) {
  return apiFetch<MeResponse>("/v1/me", { token });
}

export function listMembers(token: string | null, orgId: string) {
  return apiFetch<Member[]>(`/v1/orgs/${orgId}/members`, { token });
}

export function listSessions(token: string | null) {
  return apiFetch<Session[]>("/v1/sessions", { token });
}

export function getSession(token: string | null, sessionId: string) {
  return apiFetch<Session>(`/v1/sessions/${sessionId}`, { token });
}

export function listTurns(token: string | null, sessionId: string) {
  return apiFetch<Turn[]>(`/v1/sessions/${sessionId}/turns`, { token });
}

export function createSession(token: string | null, agentId: string) {
  return apiFetch<Session>("/v1/sessions", {
    method: "POST",
    body: { agent_id: agentId },
    token,
    headers: { "Idempotency-Key": crypto.randomUUID() },
  });
}
