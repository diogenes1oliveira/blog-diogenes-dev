# Architecture

Monorepo at repo root: shared config (TypeScript, Vite, Vitest) and multiple logical packages under `src/`.

## Top-level config

- **package.json** — scripts, dependencies, workspace (if used).
- **tsconfig.json** — TypeScript; path alias `@/*` → `./src/*` so imports like `@/feedback/client` resolve to `src/feedback/client`.
- **vite.config.ts** — Vite build and dev; same `@/` alias; Vitest in same config.

## Source layout (`src/`)

- **`src/feedback/lib`** — shared types/utilities for feedback (no runtime env).
- **`src/feedback/client`** — client-side entry (e.g. browser); can depend on `@/feedback/lib`.
- **`src/feedback/worker`** — worker entry (e.g. Cloudflare Worker); can depend on `@/feedback/lib`.

Boundaries: `lib` has no Node/browser/worker-specific code; `client` and `worker` are separate entry points and may each depend on `lib`.

## Other

- **docs/** — MkDocs site and meta docs (AGENTS, PROTOCOL, chats).
- **Site/build** — MkDocs output; separate from Vite build (Vite can emit bundles used by the site or workers).
