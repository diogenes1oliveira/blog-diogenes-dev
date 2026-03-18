import { describe, it, expect } from "vitest";
import { createFeedbackPayload } from "@/feedback/lib";

describe("createFeedbackPayload", () => {
  it("returns payload with kind and value", () => {
    const payload = createFeedbackPayload("rating", 5);
    expect(payload).toEqual({ kind: "rating", value: 5 });
  });
});
