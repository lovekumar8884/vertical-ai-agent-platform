import { API_BASE_URL, ApiError } from "./client";

export interface SseHandlers {
  onToken: (text: string) => void;
  onDone?: (endReason: string) => void;
  onError?: (message: string) => void;
}

/**
 * Consume the SSE chat stream. Aborting `signal` cancels the request; the server
 * then persists the partial assistant turn as `client_cancel` (ADR-046), and any
 * tokens already delivered remain rendered.
 */
export async function streamMessage(
  token: string | null,
  sessionId: string,
  content: string,
  handlers: SseHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/v1/sessions/${sessionId}/messages/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ content }),
      signal,
    },
  );

  if (!response.ok || !response.body) {
    throw new ApiError(response.status, null, `Stream failed (${response.status}).`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let boundary = buffer.indexOf("\n\n");
      while (boundary !== -1) {
        const frame = buffer.slice(0, boundary).trim();
        buffer = buffer.slice(boundary + 2);
        boundary = buffer.indexOf("\n\n");
        if (!frame.startsWith("data:")) continue;
        const event = JSON.parse(frame.slice(5).trim()) as {
          op: string;
          text?: string;
          message?: string;
          end_reason?: string;
        };
        if (event.op === "token" && event.text) handlers.onToken(event.text);
        else if (event.op === "done") handlers.onDone?.(event.end_reason ?? "stop");
        else if (event.op === "error") handlers.onError?.(event.message ?? "error");
      }
    }
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") return;
    throw err;
  } finally {
    reader.releaseLock();
  }
}
