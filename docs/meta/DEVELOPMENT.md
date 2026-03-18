# Development

## Setup

- **Node**: install Node.js (LTS). Dependencies: `npm install`.
- **Python**: used for some tooling; see `pyproject.toml` if applicable.
- **Just**: optional; run `just` in repo root for available commands.

## Monorepo layout

Top-level config: `package.json`, `tsconfig.json`, `vite.config.ts`. TypeScript and Vite apply to the whole repo.

- **Path alias**: `@/` resolves to repo root. Example: `import ... from '@/feedback/client'` → `src/feedback/client` (with `@/` = `./src` in config).
- **Packages under `src/`**: `src/feedback/lib`, `src/feedback/client`, `src/feedback/worker` (shared lib, client entry, worker entry).

## Scripts (package.json)

- `npm run build` — Vite build (see `vite.config.ts`).
- `npm run dev` — Vite dev server.
- `npm run test` — Vitest.
- `npm run test:run` — Vitest single run (CI).

## Testing

- **Vitest**: unit/integration tests; config in `vite.config.ts` (or `vitest.config.ts`). Use `@/` in imports in tests the same as in source.

## Docs

- **AGENTS.md** (this folder): agent conventions, chat logging, key files.
- **ARCHITECTURE.md** (repo root): high-level layout and boundaries. Update it when adding or moving packages.
