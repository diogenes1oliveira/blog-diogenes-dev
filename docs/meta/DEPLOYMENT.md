# Deployment Checklist

> Use this before going live. Tick each box, then deploy with confidence.

---

## ☑ Pre-deployment double-checks

### Privacy & confidentiality

- [ ] **Repository is set to Private.**
      The conversation logs under `dev/chats/` and protocol files contain a full record of this
      session. If you do not want it public, the repo **must** be private before you share
      the live URL with anyone.
- [ ] **No API keys, tokens, or credentials appear in any committed file.**
      Run a quick scan: `git grep -r "sk-" && git grep -r "ghp_"` — both should return nothing.
- [ ] **Per-session chat logs (`dev/chats/CHAT-XXXX.md`) do not contain anything you consider sensitive.**
      Review the conversation log. If needed, redact entries before deploying.
- [ ] **`docs/llm-parameters.md` is intentional.**
      This file documents LLM session parameters and privacy considerations.
      It is useful reference material but describes the internals of this setup.
      Decide whether you want it publicly visible.

### Site configuration

- [ ] **`mkdocs.yml` `site_url` matches your target domain.**
      Current value: `https://001481.xyz/` (for Cloudflare). Use GitHub Pages URL if you stay on Pages.
- [ ] **If using GitHub Pages:** source is set to "GitHub Actions" (`deploy.yml`) and the workflow is green.
- [ ] **If using Cloudflare Pages:** `.github/workflows/deploy-cloudflare.yml` is enabled; secrets
      `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, and `CLOUDFLARE_PAGES_PROJECT_NAME` are set; custom domain
      (e.g. 001481.xyz) is added in Cloudflare dashboard → your Pages project → Custom domains.

### Final smoke-test

- [ ] **Visit the live URL and verify the home page loads.**
- [ ] **Click through each nav item** — Home, Protocol, Agents Guide, Chat History,
      LLM Parameters — and confirm they render correctly.
- [ ] **Search works** — type a keyword in the search box and verify results appear.
- [ ] **Dark mode toggle works** — click the moon/sun icon in the top-right.

---

## Deploying to Cloudflare Pages (optional)

To serve the site from your own domain (e.g. **001481.xyz**) on Cloudflare:

1. **Workflow:** Use `.github/workflows/deploy-cloudflare.yml`. It builds with MkDocs and deploys the `site/` output to Cloudflare Pages via `wrangler-action`.
2. **Secrets:** In GitHub → Settings → Secrets and variables → Actions, add:
    - `CLOUDFLARE_API_TOKEN` (token with "Cloudflare Pages — Edit")
    - `CLOUDFLARE_ACCOUNT_ID` (from Cloudflare dashboard)
    - `CLOUDFLARE_PAGES_PROJECT_NAME` (e.g. `cine-holliu` — the name of your Pages project)
3. **Pages project:** In Cloudflare dashboard, Workers & Pages → Create → Pages → create a project (or let the first deploy create it if supported).
4. **Custom domain:** In your Pages project → Custom domains → add **001481.xyz** and follow DNS instructions.
5. **Switch over:** You can disable or remove `deploy.yml` (GitHub Pages) once Cloudflare is working. Ensure `site_url` in `mkdocs.yml` is `https://001481.xyz/`.

---

## ⚠️ What NOT to share

| Item                                           | Why                                                        |
| ---------------------------------------------- | ---------------------------------------------------------- |
| This repo URL (while public)                   | Exposes full conversation history in per-session chat logs |
| Direct link to a per-session chat log          | Contains verbatim session transcript                       |
| Your GitHub API / Copilot subscription details | Personal credentials                                       |
| The system prompt contents                     | Internal agent instructions                                |

---

## ✅ What is safe to share

| Item                                                                                  | Notes                                                                                   |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| The **live mkdocs URL** (private repo → Pages still works for users with repo access) | Only users with repository read access can view the Pages site when the repo is private |
| `./LLM-PARAMS.md` reference                                                           | Generic LLM knowledge, no credentials                                                   |
| `PROTOCOL.md`                                                                         | Agent logging spec — no personal data                                                   |

---

> _See [LLM Parameters](./LLM-PARAMS.md) for the full privacy and reproducibility analysis._
