"use client";

import { useEffect, useState } from "react";

import { listSessions, listTurns } from "@/lib/api/sessions";
import type { Session, Turn } from "@/lib/api/types";
import { useToken } from "@/lib/use-token";

export default function ConversationsPage() {
  const getToken = useToken();
  const [sessions, setSessions] = useState<Session[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [turns, setTurns] = useState<Turn[] | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await listSessions(await getToken());
        if (active) setSessions(data);
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load conversations.");
        }
      }
    })();
    return () => {
      active = false;
    };
  }, [getToken]);

  async function open(id: string) {
    setSelected(id);
    setTurns(null);
    try {
      setTurns(await listTurns(await getToken(), id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation.");
    }
  }

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="mb-6 text-xl font-semibold">Conversations</h1>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {!error && sessions === null && (
        <p className="text-sm text-muted-foreground">Loading…</p>
      )}
      {sessions?.length === 0 && (
        <p className="text-sm text-muted-foreground">No conversations yet.</p>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-[18rem_1fr]">
        <ul className="space-y-1">
          {sessions?.map((session) => (
            <li key={session.id}>
              <button
                type="button"
                onClick={() => open(session.id)}
                className={`w-full rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent ${
                  selected === session.id ? "bg-accent" : ""
                }`}
              >
                {session.id}
              </button>
            </li>
          ))}
        </ul>

        <div className="rounded-md border p-4">
          {!selected && (
            <p className="text-sm text-muted-foreground">
              Select a conversation to view its messages.
            </p>
          )}
          {selected && turns === null && (
            <p className="text-sm text-muted-foreground">Loading…</p>
          )}
          <div className="space-y-3">
            {turns?.map((turn) => (
              <div key={turn.id}>
                <div className="text-xs font-medium text-muted-foreground">
                  {turn.role}
                </div>
                <div className="whitespace-pre-wrap text-sm">{turn.content}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
