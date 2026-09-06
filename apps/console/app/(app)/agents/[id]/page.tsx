"use client";

import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { createSession } from "@/lib/api/sessions";
import { streamMessage } from "@/lib/api/sse";
import { useToken } from "@/lib/use-token";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const inputClass =
  "flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring";

export default function TestChatPage() {
  const getToken = useToken();
  const { id: agentId } = useParams<{ id: string }>();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const session = await createSession(await getToken(), agentId);
        if (active) setSessionId(session.id);
      } catch {
        if (active) setError("Could not start a Test Chat session.");
      }
    })();
    return () => {
      active = false;
    };
  }, [getToken, agentId]);

  async function send() {
    if (!sessionId || !input.trim() || streaming) return;
    const content = input.trim();
    setInput("");
    setError(null);
    setMessages((prev) => [
      ...prev,
      { role: "user", content },
      { role: "assistant", content: "" },
    ]);
    setStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;
    try {
      await streamMessage(
        await getToken(),
        sessionId,
        content,
        {
          onToken: (text) =>
            setMessages((prev) => {
              const next = [...prev];
              const last = next[next.length - 1];
              next[next.length - 1] = { role: "assistant", content: last.content + text };
              return next;
            }),
          onError: (message) => setError(message),
        },
        controller.signal,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Streaming failed.");
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-3xl flex-col">
      <h1 className="mb-4 text-xl font-semibold">Test Chat</h1>

      <div className="flex-1 space-y-3 overflow-y-auto rounded-md border p-4">
        {messages.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Send a message to test this agent.
          </p>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            className={message.role === "user" ? "text-right" : "text-left"}
          >
            <span
              className={`inline-block whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
                message.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              }`}
            >
              {message.content || (streaming ? "…" : "")}
            </span>
          </div>
        ))}
      </div>

      {error && <p className="mt-2 text-sm text-destructive">{error}</p>}

      <div className="mt-4 flex gap-2">
        <input
          className={inputClass}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") send();
          }}
          placeholder={sessionId ? "Type a message…" : "Starting session…"}
          disabled={!sessionId}
        />
        {streaming ? (
          <Button type="button" variant="outline" onClick={() => abortRef.current?.abort()}>
            Stop
          </Button>
        ) : (
          <Button type="button" onClick={send} disabled={!sessionId || !input.trim()}>
            Send
          </Button>
        )}
      </div>
    </div>
  );
}
