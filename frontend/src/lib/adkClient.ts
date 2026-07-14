/**
 * Minimal ADK REST client — blueprint skeleton.
 * Talks to `adk api_server` locally; swap ADK_API_BASE_URL for the
 * Agent Engine endpoint at deployment — nothing else changes.
 */
const ADK_API_BASE_URL = process.env.ADK_API_BASE_URL ?? "http://localhost:8000";
const ADK_APP_NAME = "app";

export async function ensureSession(userId: string, sessionId: string): Promise<void> {
  // POST /apps/:app/users/:userId/sessions/:sessionId — idempotent create.
  await fetch(
    `${ADK_API_BASE_URL}/apps/${ADK_APP_NAME}/users/${userId}/sessions/${sessionId}`,
    { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" },
  );
}

export interface AgentTurn {
  reply: string;
  chart: unknown | null; // declarative chart spec — the UI renders, the model never draws
}

export async function runAgent(userId: string, sessionId: string, message: string): Promise<AgentTurn> {
  const res = await fetch(`${ADK_API_BASE_URL}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      appName: ADK_APP_NAME,
      userId,
      sessionId,
      newMessage: { role: "user", parts: [{ text: message }] },
    }),
  });
  const events: any[] = await res.json();

  // The final answer is the LAST event with role "model" and a text part;
  // a fenced chart JSON block, when present, is extracted into `chart`.
  const final = [...events].reverse()
    .find((e) => e.content?.role === "model" && e.content?.parts?.some((p: any) => p.text));

  throw new Error("Blueprint stub — chart extraction omitted");
}
