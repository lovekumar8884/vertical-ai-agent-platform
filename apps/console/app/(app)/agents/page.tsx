"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { listAgents } from "@/lib/api/agents";
import type { Agent } from "@/lib/api/types";
import { useToken } from "@/lib/use-token";

export default function AgentsPage() {
  const getToken = useToken();
  const [agents, setAgents] = useState<Agent[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await listAgents(await getToken());
        if (active) setAgents(data);
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load agents.");
        }
      }
    })();
    return () => {
      active = false;
    };
  }, [getToken]);

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Agents</h1>
        <Button asChild>
          <Link href="/agents/new">New agent</Link>
        </Button>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}
      {!error && agents === null && (
        <p className="text-sm text-muted-foreground">Loading…</p>
      )}
      {agents?.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No agents yet. Create your first agent to start a Test Chat.
        </p>
      )}

      <div className="grid gap-3">
        {agents?.map((agent) => (
          <Link key={agent.id} href={`/agents/${agent.id}`}>
            <Card className="transition-colors hover:bg-accent">
              <CardHeader>
                <CardTitle>{agent.name}</CardTitle>
                <CardDescription>
                  {agent.status} · {agent.slug}
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
