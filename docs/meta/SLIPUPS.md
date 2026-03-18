# AI Agent Slip-ups & Lessons

This document tracks common pitfalls, edge-cases, and mistakes made by AI agents working on this repository. Reading this helps prevent repeating past errors.

## 1. Misplaced Chat Logs

**The Slip-up:** Logs were incorrectly created under `docs/dev/chats/` instead of `docs/meta/chats/`.

**The Cause:** Outdated references in `AGENTS.md` and `PROTOCOL.md` instructed agents to put chat log files in `docs/dev/chats/`. The agent followed the written guidelines verbatim, ignoring that actual log files were located in `docs/meta/chats/`.

**The Fix:**
- Updated `PROTOCOL.md` and `AGENTS.md` to point to the correct directory (`docs/meta/chats/`).
- Moved misplaced logs (e.g. `CHAT-0001.md` created there) to `docs/meta/chats/CHAT-XXXX.md` with the next sequential number.
- Removed the incorrectly created `docs/dev/chats/` directory.

**Lesson:** Always cross-reference instructions in meta docs with the actual repository state. If a doc says one directory, but the files clearly live in another, ask for clarification or update the documentation to match reality.

---

## 2. MkDocs Material Template Overrides

**The Slip-up:** Extending `blog-post.html` inside `overrides/blog-post.html` using `{% extends "blog-post.html" %}`, which resulted in infinite recursion (maximum recursion depth exceeded).

**The Cause:** Material for MkDocs `custom_dir` (overrides directory) files **replace** the original file in the Jinja search path. When `overrides/blog-post.html` asks Jinja to extend `blog-post.html`, it includes itself instead of the base theme's template.

**The Fix:**
- Do not use `{% extends "template-name.html" %}` in a file of the **exact same name** inside `overrides/`.
- Instead, make the override template a full copy of the original theme's template, appending the new custom blocks to it. (And let it extend `main.html`, just like the original).

**Lesson:** When overriding MkDocs Material templates via `custom_dir`, files of the same name replace the original completely, rather than extending them. 
