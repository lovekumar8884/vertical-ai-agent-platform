"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { createAgent } from "@/lib/api/agents";
import { useToken } from "@/lib/use-token";

const inputClass =
  "w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring";

export default function NewAgentPage() {
  const getToken = useToken();
  const router = useRouter();
  const [name, setName] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!name.trim() || !systemPrompt.trim()) {
      setError("Name and system prompt are required.");
      return;
    }
    setSubmitting(true);
    try {
      const agent = await createAgent(await getToken(), {
        name: name.trim(),
        system_prompt: systemPrompt.trim(),
        temperature,
      });
      router.push(`/agents/${agent.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create agent.");
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-xl font-semibold">New agent</h1>
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1.5 text-sm font-medium">
          Name
          <input
            className={inputClass}
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={120}
            placeholder="Clinic Front Desk"
          />
        </label>

        <label className="flex flex-col gap-1.5 text-sm font-medium">
          System prompt
          <textarea
            className={`${inputClass} min-h-40`}
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="You are a helpful receptionist for…"
          />
        </label>

        <label className="flex flex-col gap-1.5 text-sm font-medium">
          Temperature: {temperature.toFixed(1)}
          <input
            type="range"
            min={0}
            max={1}
            step={0.1}
            value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
          />
        </label>

        <p className="text-xs text-muted-foreground">Model: gpt-4o-mini</p>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <div className="flex gap-2">
          <Button type="submit" disabled={submitting}>
            {submitting ? "Creating…" : "Create agent"}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push("/agents")}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
