/**
 * Client-side feedback entry. Use from browser or other client runtimes.
 */

import { createFeedbackPayload } from "@/feedback/lib";

export function submitFeedback(kind: string, value: unknown): void {
  const payload = createFeedbackPayload(kind, value);
  console.log("[feedback/client] submit", payload);
}

export { createFeedbackPayload } from "@/feedback/lib";

export function bindFeedback(
  form: HTMLElement | string,
  selectedClassName?: string | undefined | null
) {
}
