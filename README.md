# Shiplog

> **You ship → Shiplog reads what you did → writes the posts in your voice → you approve → you post.**

Shiplog is an AI-powered build-in-public automation tool for developers. When you push code to GitHub, Shiplog reads the **actual code diff** (not just the commit message), decides whether the change is worth posting about, and — if it is — generates ready-to-publish content in your own voice.

No auto-posting. Everything lands in a review queue where you edit and approve before anything goes public. Over time, Shiplog learns your writing style from your edits, so drafts need less correction.

---

## Why Shiplog exists

After building something, you still have to:

- Think of what to post
- Write it for X
- Rewrite it for LinkedIn
- Maybe write a blog post too

That context-switching kills momentum. Shiplog automates the gap between `git push` and "I shipped something today."

### What makes it different

Existing tools (CommitToX, Posterly, n8n templates) take the commit *message string* and rephrase it. That's shallow. Shiplog:

- Reads the **actual code diff** — so it can say "added JWT auth with bcrypt hashing" even when your commit message was just `add login`
- Distinguishes a typo from a milestone — no noise
- Generates **multi-format output** (X + LinkedIn + dev.to + README)
- **Learns and matches your personal voice** from your edits over time

---

## How it works

```
git push
    │
    ▼
GitHub webhook fires
    │
    ▼
Stage 2 — Gate (signature check → event type → branch filter)
    │
    ▼
Stage 3 — Enrich (fetch actual diff via GitHub API)
    │
    ▼
Stage 4 — Classify (trivial / medium / milestone)
    │
    ▼
Stage 5 — Generate (X post / LinkedIn / dev.to draft / README update)
    │
    ▼
Stage 6 — Review queue (you edit and approve — nothing auto-posts)
    │
    ▼
Stage 7 — One-click copy / publish
    │
    ▼
Stage 8 — Log to history (idempotent by commit SHA)
```

### The three tiers

| Tier | What it means | Example | Output |
|------|--------------|---------|--------|
| **Trivial** | Not worth posting about | Typo fix, formatting, variable rename | Nothing (logged only) |
| **Medium** | A real but small win | One feature added, a notable bug fixed | X post only |
| **Milestone** | A big deal | Shipped a whole feature, hit v1.0 | X + LinkedIn + dev.to + README |

Tier is decided by the **LLM reading the diff** by default — not by commit count, not by you typing `[ship]`. Keywords like `[ship]` and `[skip]` exist as optional manual overrides only.

---

## Tech stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Backend | FastAPI (Python) | Webhook receiver + pipeline + dashboard API |
| Database | PostgreSQL (Neon) | Multi-user-ready from day one; stateful (drafts, history, style profiles) |
| LLM | Gemini Flash | ~1,500 req/day free tier; 1M token context; swappable wrapper |
| Frontend | React + Tailwind | Dashboard / review feed |
| Hosting | Render + UptimeRobot | Free tier + keep-alive ping (cold-start safe) |
| External APIs | GitHub API, dev.to API | Diff fetch, README commits, draft push |

---

## Current build status

Shiplog is being built stage by stage. Current progress:

- [x] **Stage 2 — Webhook receiver**
  - HMAC-SHA256 signature verification
  - Event-type filter (`push` only)
  - Branch/ref filter (main only)
  - Deletion and force-push handling
  - `PushEvent` SQLAlchemy model defined
  - Delivery ID deduplication (prevent double-processing on GitHub retries)
- [ ] **Database wiring** — Neon setup → engine/session → Alembic migration → save to DB
- [ ] Stage 3 — Diff enrichment (GitHub API)
- [ ] Stage 4 — Classifier
- [ ] Stage 5 — Generator
- [ ] Stage 6 — Review feed (dashboard)
- [ ] Stage 7 — One-click copy / dev.to push / README commit
- [ ] Stage 8 — History log
- [ ] Learning loop (style profile)
- [ ] Batching / digest ("wrap up my day")