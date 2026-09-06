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

export interface Agent {
  id: string;
  slug: string;
  name: string;
  status: "draft" | "published";
}

export interface AgentCreate {
  name: string;
  system_prompt: string;
  temperature?: number;
}

export interface Session {
  id: string;
  agent_id: string;
  agent_version_id: string;
  channel: string;
}

export interface Turn {
  id: string;
  idx: number;
  role: string;
  content: string;
}

export interface OrgSummary {
  id: string;
  slug: string;
  name: string;
}

export interface UserSummary {
  id: string;
  email: string;
  name: string | null;
}

export interface Membership {
  id: string;
  role: string;
  org: OrgSummary;
}

export interface MeResponse {
  user: UserSummary;
  memberships: Membership[];
}

export interface Member {
  id: string;
  role: string;
  user: UserSummary;
}
