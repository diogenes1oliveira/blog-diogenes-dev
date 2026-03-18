/**
 * Shared types and utilities for feedback. No runtime env (browser/worker) specifics.
 */

export type FeedbackType = "like" | "like_undo" | "dislike" | "dislike_undo" | "skipped";

export type FeedbackPayload = {
  buffers: Record<FeedbackType, string>,
}

export function submitLike() {
  payload
}
