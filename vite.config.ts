import path from "path";
import { fileURLToPath } from "url";
import { defineConfig } from "vitest/config";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  build: {
    lib: {
      entry: {
        "feedback-client": path.resolve(__dirname, "src/feedback/client/index.ts"),
        "feedback-worker": path.resolve(__dirname, "src/feedback/worker/index.ts"),
      },
      formats: ["es"],
    },
    rollupOptions: {
      external: [],
    },
  },
  test: {
    globals: true,
    environment: "node",
  },
});
