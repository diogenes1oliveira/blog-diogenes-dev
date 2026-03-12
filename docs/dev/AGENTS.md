# AGENTS.md

## Prompt History Convention

Every time an agent works on this repository, it **must** append both sides of
the current conversation turn to [dev/CHATS.md](CHATS.md) as two separate, fenced plaintext
code blocks — **in this order**:

1. **User block** — the exact user message that triggered this session.
2. **Agent block** — a concise summary of what the agent did / replied.

### Format

```markdown

```

<user message verbatim>
```

```
<agent response summary>
```

````

### Rules

- Always append to the **end** of `PROMPT.md`; never edit existing blocks.
- Use plain fenced code blocks (triple backticks, no language tag).
- Keep the agent block short but informative (one or a few sentences).
- Do this **before** calling `report_progress` for the final commit so that
  the turn is included in the same commit as the rest of the changes.

---

## ⚠️ CHATS.md Convention — PRIMARY PROTOCOL (supersedes PROMPT.md) ⚠️

**Every agent session must update `CHATS.md`** — the canonical conversation log.
The `PROMPT.md` section above is **legacy**; once `PROTOCOL.md` exists, skip it.

### CHATS.md turn structure

```markdown
## Turn #N — <short description>

### Message #0 — @human

```
<verbatim human text — no formatting, no language tag>
```

### Message #1 — Agent

<formatted markdown prose: `code` spans, **bold**, lists, etc.>

```markdown
<verbatim agent reply, all markdown formatting preserved>
```

#### THOUGHTS

<optional: short note on the agent’s reasoning for this turn — “how the brain worked”, e.g. what was considered, what was rejected, why. Kept brief. Omit if none to record.>
````

### Rules (memorise these)

1. **Human is always `#0`** and always starts every turn.
2. **Human blocks**: plain ` ``` ` fence, no language tag, verbatim text only.
3. **Agent blocks**: formatted markdown prose **+** the agent's **full, complete, verbatim**
   response inside a ` ```markdown ` fence. Not a summary — the entire reply.
4. **Turn numbers** are sequential from 1 — never skip or reuse.
5. **Missing turns** → reconstruct from `PROMPT.md`, commit history, and context.
   Mark reconstructed messages with `<!-- reconstructed -->` on the header line.
6. **Gap detection**: `## Turn #` lines must be sequential; every turn must have
   `### Message #0`. A missing `#0` or a gap in N means a turn needs filling.
7. **Parsing turns**: scan for `## Turn #N` → extract N as integer → content ends
   at next `## Turn #` or EOF.
8. **Parsing messages**: within a turn, scan for `### Message #M` → extract M →
   content ends at next `### Message #` or `## Turn #` or EOF.
9. **Do this before `report_progress`** — the turn must be in the same commit.
10. **THOUGHTS**: after the ` ```markdown ` block, add `#### THOUGHTS` (four `#`) with a short
    note on the agent's reasoning for the turn — what was considered, what was rejected, why
    (like "showing how the brain works"). Optional but encouraged; omit if nothing to record.
11. **Files Accessed**: after THOUGHTS (or after the verbatim block if THOUGHTS omitted), add
    `#### Files Accessed` listing every repo-local file path read, created, or modified — one
    bullet per file with a brief note. Omit if no repo files were accessed. Mark
    `<!-- reconstructed -->` on the header for past turns.

---

## Key Project Files

Files every agent should know exist in this repository:

| File                     | Purpose                                                                             |
| ------------------------ | ----------------------------------------------------------------------------------- |
| `PROMPT.md`              | Legacy per-turn conversation log (append-only, superseded by `CHATS.md`)            |
| `CHATS.md`               | Canonical conversation log — primary protocol                                       |
| `PROTOCOL.md`            | Self-contained spec for the `CHATS.md` format                                       |
| `AGENTS.md`              | This file — conventions and key-file reference for agents                           |
| `EASTEREGG.md`           | Launch easter egg: lights-off (📴) terminal-style alert `$ ⏎` + upcoming issue note |
| `docs/index.md`          | Main documentation home page                                                        |
| `docs/dev/LLM-PARAMS.md` | LLM session-parameters reference (privacy, exposure, reproducibility)               |
| `docs/ci/DEPLOYMENT.md`  | Pre-flight deployment checklist                                                     |
| `mkdocs.yml`             | MkDocs site configuration and nav                                                   |
