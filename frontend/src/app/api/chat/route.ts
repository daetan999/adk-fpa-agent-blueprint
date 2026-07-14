import { NextRequest, NextResponse } from "next/server";
import { ensureSession, runAgent } from "@/lib/adkClient";

// Server-side proxy: the ADK endpoint stays private to the server runtime;
// the browser only ever sees this route.
export async function POST(req: NextRequest) {
  const { message, userId, sessionId } = await req.json();

  if (!message || !userId || !sessionId) {
    return NextResponse.json(
      { error: "message, userId, and sessionId are required" },
      { status: 400 },
    );
  }

  try {
    await ensureSession(userId, sessionId);
    const { reply, chart } = await runAgent(userId, sessionId, message);
    return NextResponse.json({ reply, chart });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Unknown error" },
      { status: 502 },
    );
  }
}
