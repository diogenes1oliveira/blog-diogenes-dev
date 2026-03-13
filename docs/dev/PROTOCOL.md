# PROTOCOL.md — Agent Conversation Logging Protocol

This is the **canonical, self-contained spec** for logging conversations in this repository.
Every agent session must follow it. Reading `AGENTS.md` or `PROMPT.md` is optional context;
this file is sufficient.

---

## 1. Canonical logs: per-session `CHAT-XXXX.md` files

The canonical conversation logs live in **per-session files** under `docs/dev/chats/`,
one file per agent session, named `CHAT-XXXX.md` (see section 6).

`CHATS.md` and `PROMPT.md` are legacy/aggregate logs:

- Do **not** create or update `PROMPT.md` for new work.
- Do **not** create or update `CHATS.md` for new work unless explicitly asked.

---

## 2. CHATS.md format (legacy)

### 2.1 Turn header

Every exchange between the human and the agent is a **turn**.
Turns are numbered sequentially starting from 1.

```
## Turn #N — <short description of the turn>
```

- `N` is a positive integer, sequential, never skipped or reused.
- The description is a brief (≤ 10 words) summary of what happened.

### 2.2 Human message (always Message #0)

The human **always** starts a turn. Their message is recorded verbatim, with no
formatting changes, inside a plain fenced code block (no language tag):

```
### Message #0 — @human

` ``
<verbatim human text — no markdown, no reformatting>
` ``
```

_(Remove the spaces inside the backtick sequences above.)_

### 2.3 Agent message (Message #1 or higher)

Agent responses consist of two parts:

1. **Prose** — a nicely formatted markdown summary using `code` spans for technical
   terms, **bold** for emphasis, lists for enumerations, etc.
2. **Verbatim block** — the agent's **complete, full** reply inside a fenced `markdown`
   block. This must be the **entire** agent response — every word, every code block,
   every list — verbatim. Not a summary. Not a paraphrase. The whole thing.

3. **THOUGHTS** (optional) — a short note on the agent's reasoning for this turn: what was
   considered, what was rejected, why. "How the brain worked." Use `#### THOUGHTS` (four `#`),
   placed **right below** the verbatim ` ```markdown ` block. Omit if there is nothing to record.

````
### Message #1 — Agent

<formatted markdown prose>

` ```markdown
<verbatim agent reply, all markdown preserved: code blocks, bold, lists, etc.>
` ```

#### THOUGHTS

<optional: agent reasoning for this turn — brief. Omit if none.>
````

_(Remove the spaces inside the backtick sequences above.)_

### 2.4 Files Accessed (agent message footnote)

After the verbatim ` ```markdown ` block, every agent message must include a
`#### Files Accessed` subsection listing the repo-local file paths that were read,
created, or modified during the turn. Use one bullet per file with a brief note.

```
#### Files Accessed

- `path/to/file` — brief note (e.g. "read", "created", "updated")
```

- Use `#### ` (four `#`) — one level deeper than the `###` message header.
- List **only files within this repository** (not external URLs or APIs).
- For reconstructed turns, append `<!-- reconstructed -->` to the header line.
- If no repo files were accessed, omit the section entirely.

---

### 3.1 Normal update (current turn)

Before calling `report_progress` for the final commit:

1. Determine the next turn number N (last `## Turn #N` in the file + 1, or 1 if empty).
2. Append a new turn block with:
    - `## Turn #N — <description>`
    - `### Message #0 — @human` with the verbatim human message.
    - `### Message #1 — Agent` with the formatted prose + verbatim block.

### 3.2 Retroactive reconstruction

When `CHATS.md` is first created, or when gap turns are detected (for legacy logs only):

1. **Check for gaps**: scan `## Turn #N` headers — if N values are not sequential,
   turns are missing. Also check that every turn has a `### Message #0 — @human`.
2. **Reconstruct**: use `PROMPT.md`, commit messages, PR descriptions, and any
   context in memory to reconstruct missing turns with best effort.
3. **Mark reconstructions**: add `<!-- reconstructed -->` immediately after the
   `### Message #M — Role` header of any message reconstructed rather than logged live.

---

## 4. Parsing algorithm

To read or update `CHATS.md` programmatically (for legacy logs):

```python
turns = {}
current_turn = None
current_message = None

for line in chats_md_lines:
    if line.startswith("## Turn #"):
        # e.g. "## Turn #3 — Mirror repo" → N = 3
        parts = line.split("#")
        if len(parts) >= 3:
            n = int(parts[2].split()[0])
            current_turn = n
            turns[n] = {"title": line.strip(), "messages": {}}
            current_message = None

    elif line.startswith("### Message #") and current_turn is not None:
        # e.g. "### Message #1 — Agent" → M = 1
        parts = line.split("#")
        if len(parts) >= 3:
            m = int(parts[2].split()[0])
            current_message = m
            turns[current_turn]["messages"][m] = {"header": line.strip(), "body": ""}

    elif current_turn is not None and current_message is not None:
        turns[current_turn]["messages"][current_message]["body"] += line
```

**Turn boundaries**: `## Turn #N` to next `## Turn #` or EOF.
**Message boundaries**: `### Message #M` to next `### Message #` or `## Turn #` or EOF.

---

## 5. Quick-reference cheat sheet

| Element                 | Format                                                       |
| ----------------------- | ------------------------------------------------------------ |
| Turn header             | `## Turn #N — <description>`                                 |
| Human message header    | `### Message #0 — @human`                                    |
| Agent message header    | `### Message #1 — Agent`                                     |
| Human body              | plain ` ``` ` fence, verbatim, no language tag               |
| Agent body              | markdown prose + verbatim inside ` ```markdown ` fence       |
| THOUGHTS (optional)     | `#### THOUGHTS` — short note on agent reasoning for the turn |
| Files Accessed footnote | `#### Files Accessed` — one bullet per repo file, brief note |
| Reconstructed message   | `<!-- reconstructed -->` after the `### Message` header      |
| When to update          | before `report_progress`, same commit as other changes       |
| Source of truth         | Per-session `docs/dev/chats/CHAT-XXXX.md` files              |

---

## 6. Per-session chat files in `docs/dev/chats/`

In addition to any legacy aggregate `CHATS.md` log, every **agent session** (a single interactive chat run in Cursor)
must be logged in its own file under `docs/dev/chats/`.

### 6.1 File naming and index

- **Directory**: `docs/dev/chats/`
- **Naming**: `CHAT-XXXX.md` where `XXXX` is a zero-padded integer:
  - `CHAT-0001.md`, `CHAT-0002.md`, `CHAT-0003.md`, …
- **Index file**: `docs/dev/chats/devindex.md` keeps a table of all session files:

  ```markdown
  | Index | File                         |
  | ----- | ---------------------------- |
  | 1     | [CHAT-0001.md](CHAT-0001.md) |
  | 2     | [CHAT-0002.md](CHAT-0002.md) |
  | 3     | [CHAT-0003.md](CHAT-0003.md) |
  ```

- **Append-only**:
  - When starting a **new agent session**, create a new `CHAT-XXXX.md` with the next number.
  - Append a new row to `devindex.md` with the next sequential `Index` and a link to the file.
  - Never rename or reuse an existing `CHAT-XXXX.md`.

### 6.2 Session file header

Each per-session file starts with:

```markdown
# Chat #N — Conversation Logs

Canonical conversation log for this repository.
See [PROTOCOL.md](../PROTOCOL.md) for the format specification.

---
```

- `N` is the same integer used in the filename `CHAT-XXXX.md` (without zero-padding).

### 6.3 Session file contents

Inside each `CHAT-XXXX.md`:

- Use **exactly** the same turn/message format as in sections 2–3:
  - `## Turn #N — <description>`
  - `### Message #0 — @human` with plain fenced code block (no language tag)
  - `### Message #1 — Agent` with formatted prose + verbatim ` ```markdown ` block
  - Optional `#### THOUGHTS`
  - Required `#### Files Accessed` when repo files are touched
- Treat each per-session file as **append-only**, except when retroactively reconstructing
  missing turns or messages (use `<!-- reconstructed -->` markers as usual).

`CHATS.md` may aggregate turns across sessions; `docs/dev/chats/CHAT-XXXX.md` files
provide the per-session view. Both should remain consistent with this protocol.
