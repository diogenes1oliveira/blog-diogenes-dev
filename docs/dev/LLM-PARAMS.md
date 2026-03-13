# LLM Session Parameters — Privacy Reference

> **Context:** This document was written for a GitHub Copilot Coding Agent session
> (`cine-holliu` repository). It explains the parameters that characterise an LLM
> conversation, which of them are observable from the outside, and how to harden
> your setup if you want to minimise the surface area for reproduction or surveillance.

---

## 1. Parameters that characterise an LLM session

| Parameter                              | What it controls                                                                                                                                    | Typical range / values                                   |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Model version**                      | Which exact model checkpoint is used. Different versions produce different outputs even with identical inputs.                                      | `gpt-4o-2024-11-20`, `claude-3-5-sonnet-20241022`, etc.  |
| **Temperature**                        | How "random" the sampling is. 0 = deterministic (greedy), 2 = very creative/chaotic.                                                                | `0.0` – `2.0` (OpenAI), `0.0` – `1.0` (Anthropic)        |
| **Top-p (nucleus sampling)**           | Alternative to temperature: considers only the smallest set of tokens whose cumulative probability ≥ p. Usually you set one or the other, not both. | `0.0` – `1.0`                                            |
| **Frequency penalty**                  | Reduces the probability of repeating tokens that have already appeared, proportionally to their count.                                              | `-2.0` – `2.0` (OpenAI)                                  |
| **Presence penalty**                   | Binary version of frequency penalty — penalises any token that has appeared at all, regardless of count.                                            | `-2.0` – `2.0` (OpenAI)                                  |
| **Max tokens (max completion tokens)** | Hard cap on the output length per response.                                                                                                         | 1 – model-max (e.g. 16 384 for `gpt-4o`)                 |
| **Context window**                     | Total token budget for input + output. Determines how much conversation history the model can "see".                                                | 8 k – 1 M+ tokens depending on model                     |
| **System prompt**                      | The invisible first message that tells the model who it is, what rules to follow, what tools it has. The single most powerful lever.                | Arbitrary text; usually 500–5 000 tokens                 |
| **Tools / function schemas**           | The JSON schemas of callable functions the model can invoke (file read/write, search, shell, etc.).                                                 | OpenAI `tools` array, Anthropic `tools` array            |
| **Embeddings model version**           | Used for semantic search / RAG. Turns text into vectors. Different versions produce different vector spaces.                                        | `text-embedding-3-small`, `text-embedding-3-large`, etc. |
| **UTC timestamp (injected)**           | Most system prompts inject the current date/time. If you know when the conversation happened, you can anchor the model's "now".                     | ISO-8601 UTC string                                      |
| **Seed**                               | Some APIs (OpenAI) accept a `seed` integer for pseudo-deterministic outputs at temperature 0.                                                       | Any integer                                              |

---

## 2. Which parameters are exposed — and how

### 2.1 What's visible in the public repo / PR

If the repo is **public**, anyone with the PR link can see:

- Every file committed by the agent (including any per-session `CHAT-XXXX.md` logs, which contain the full conversation for that session).
- Commit messages, PR description, and the diff.
- **Nothing** about temperature, system prompt, model version, or seed — those never appear in Git.

Making the repo **private** hides all of this from non-collaborators. That's the simplest and most effective lever.

### 2.2 What's visible via GitHub / OpenAI APIs

| Endpoint                                          | What it reveals                                                                             | Auth required             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------- |
| `GET https://api.github.com/repos/{owner}/{repo}` | Repo metadata (public or private, topics, etc.) — **not** LLM params                        | Public token or anonymous |
| `GET https://api.openai.com/v1/models`            | List of available models — **not** session params                                           | OpenAI API key            |
| `GET https://api.openai.com/v1/models/{model}`    | Model metadata — **not** your temperature or system prompt                                  | OpenAI API key            |
| GitHub Copilot API                                | No public endpoint exposes temperature, system prompt, or seed for a specific agent session | n/a                       |

**Verdict:** There is no API endpoint that lets an outsider — given only a PR link or a repo URL — query your temperature, system prompt, or model version. These are private to the API caller (GitHub's infrastructure in this case).

### 2.3 MITM / traffic interception

This is the "actually dangerous" path you hinted at with `mitmproxy`.

```
[Your browser / IDE]
        |
        | HTTPS (TLS)
        |
[GitHub Copilot servers]   ← system prompt lives here
        |
        | HTTPS (TLS)
        |
[LLM provider API]         ← temperature, model, seed live in the request body
```

A **MITM proxy** (mitmproxy, Burp Suite, Charles) inserted between your client and GitHub could intercept:

- The raw API request body → reveals `temperature`, `model`, `tools`, `max_tokens`, and crucially **the system prompt**.
- The raw API response → reveals `model` version actually used, token counts, and `system_fingerprint` (OpenAI's internal build hash).

However, inserting a MITM between your machine and GitHub requires:

1. Installing a **trusted root certificate** on your machine (so the proxy can re-sign TLS).
2. Routing your traffic through the proxy.
3. Access to the machine making the requests.

For the **GitHub Copilot Coding Agent** specifically, the agent runs on GitHub's own infrastructure — not on your machine. So a local MITM is irrelevant: you would need to intercept GitHub's own server-to-server calls, which is not feasible without GitHub's cooperation.

### 2.4 OpenAI `system_fingerprint`

OpenAI's chat completion API returns a `system_fingerprint` field in every response. It's an opaque string like `fp_a49d71c1e7` that encodes the model version and server-side configuration. Two responses with the same `system_fingerprint` were produced by the same model build. This is useful for reproducibility auditing, but it doesn't reveal temperature or system prompt.

---

## 3. Reproducibility: how hard is it?

Even if someone had **all** the parameters listed in section 1, exact reproduction of an LLM conversation is **theoretically impossible** for temperature > 0 and **practically very hard** even at temperature = 0 (due to floating-point non-determinism across GPU runs, load-balanced inference clusters, etc.).

At best, with all parameters + conversation history + seed + temperature = 0, you get **statistically similar** outputs — not byte-identical.

The conversation history itself (the messages) is the **most important** factor for reproducibility, since that's what conditions the model's outputs. If the per-session chat logs (e.g. `docs/dev/chats/CHAT-0001.md`, …) are public, that's what gives someone the best chance.

---

## 4. Mitigation checklist

| Risk                                                      | Mitigation                                                                                                                                                                             |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Someone reads the conversation via the repo               | **Set repo to private.** Already decided.                                                                                                                                              |
| Someone reads the conversation via a shared screen / link | Private repo + no link sharing. Revoke collaborator access after the session.                                                                                                          |
| Someone queries the model version via API                 | Not possible without your API key — no public endpoint exposes per-session params.                                                                                                     |
| Someone intercepts traffic with a MITM proxy              | Not applicable for server-side agent runs. For client-side Copilot (IDE), use certificate pinning or VPN.                                                                              |
| Someone infers the system prompt by probing the model     | "Prompt extraction" attacks — ask the model to repeat its instructions. Mitigation: the system prompt usually instructs the model to refuse. Nothing you can enforce on GitHub's side. |
| Per-session `CHAT-XXXX.md` logs leak the conversation     | Keep repo private. Optionally encrypt sensitive turns before committing.                                                                                                               |
| `system_fingerprint` reveals model build                  | Low risk; fingerprint doesn't expose temperature or system prompt. Acceptable.                                                                                                         |

---

## 5. The parameters you mentioned — quick reference

| You mentioned        | Technical name                            | Exposable?                                | Via what                     |
| -------------------- | ----------------------------------------- | ----------------------------------------- | ---------------------------- |
| Temperature          | `temperature`                             | Only via MITM on client-side              | mitmproxy, Burp Suite        |
| System prompt        | `messages[0].content` where `role=system` | Only via MITM or prompt extraction        | mitmproxy; asking the model  |
| Model version        | `model` (request) / `model` (response)    | Via MITM or `system_fingerprint`          | mitmproxy; response metadata |
| Embeddings version   | Separate API call's `model` param         | Only if embeddings are called client-side | mitmproxy                    |
| Current UTC time     | Injected into system prompt               | Via MITM (see system prompt)              | mitmproxy                    |
| Conversation history | `messages` array                          | Via public repo / per-session chat logs   | GitHub; browser              |

---

## 6. Example: what a `curl` probe looks like (and why it fails for session params)

```bash
# List available models — public info, no session params
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | jq '.data[].id'

# Get model metadata — still no temperature, no system prompt
curl https://api.openai.com/v1/models/gpt-4o \
  -H "Authorization: Bearer $OPENAI_API_KEY" | jq .

# There is NO endpoint like this:
# GET /v1/sessions/{session_id}/parameters  ← does not exist
```

The OpenAI (and Anthropic) REST APIs are **stateless** — there is no "session object" server-side that stores your temperature and system prompt after the request is done. Each request carries its own parameters and they are not persisted in a queryable form.

---

> _Written for Turn #10 of the `cine-holliu` conversation log._
> _See the per-session chat logs under `docs/dev/chats/` for the full thread._
