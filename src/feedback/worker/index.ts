/**
 * Worker-side feedback entry. Use from Cloudflare Worker or similar.
 */

import { createFeedbackPayload } from "@/feedback/lib";

export function handleFeedbackRequest(kind: string, value: unknown): Response {
  const payload = createFeedbackPayload(kind, value);
  return new Response(JSON.stringify(payload), {
    headers: { "Content-Type": "application/json" },
  });
}

export { createFeedbackPayload } from "@/feedback/lib";
