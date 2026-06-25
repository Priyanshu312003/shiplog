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

---

## Project structure

```
shiplog/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   └── events.py        # PushEvent SQLAlchemy model
│   ├── routers/
│   │   └── webhooks.py      # Webhook receiver endpoint
│   ├── core/
│   │   └── config.py        # Pydantic settings (env vars)
│   └── db/
│       ├── engine.py        # SQLAlchemy engine (coming soon)
│       └── session.py       # DB session dependency (coming soon)
├── alembic/
│   ├── env.py               # Alembic migration environment
│   └── versions/            # Migration files
├── alembic.ini              # Alembic config
├── requirements.txt
└── .env                     # Local secrets (never committed)
```

---

## Local setup

### Prerequisites

- Python 3.12+
- A [Neon](https://neon.tech) account (free tier) for PostgreSQL
- A GitHub repo with a webhook pointed at your server

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/Priyanshu312003/shiplog.git
cd shiplog
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root (never commit this):

```env
WEBHOOK_SECRET=your_github_webhook_secret
DATABASE_URL=postgresql://user:password@your-neon-host/shiplog
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be live at `http://localhost:8000`.

---

## Registering the GitHub webhook

1. Go to your GitHub repo → **Settings → Webhooks → Add webhook**
2. Set **Payload URL** to your server's public URL + `/webhook` (e.g. `https://your-app.onrender.com/webhook`)
3. Set **Content type** to `application/json`
4. Set **Secret** to the same value as `WEBHOOK_SECRET` in your `.env`
5. Under events, select **Just the push event**
6. Click **Add webhook**

> **Note:** for local development, use [ngrok](https://ngrok.com) or [smee.io](https://smee.io) to expose your local server to GitHub.

---

## The learning loop

Shiplog gets better at writing in your voice over time. Here's how:

1. **Every draft is generated using your current style profile** — a living document of rules, not raw examples.
2. **When you approve a post after editing it**, Shiplog compares your version to the original draft.
3. **A small LLM call decides** whether the edit was a *style preference* ("no emojis", "prefer simple verbs") or a *fact correction* ("wrong framework name"). Only style signals are kept.
4. **The rule is extracted and stored** — not the raw edit. e.g. `"removed rocket emoji"` → `"no emojis in technical posts"`.
5. **You confirm before anything is saved** to your profile — Shiplog never silently auto-learns.

Example style profile after a few weeks:

```
## X post style profile
- lowercase, casual tone
- use arrow lists (→) for wins
- one technical insight per post, no fluff
- NO emojis
- NO "what do you think?" closers
- prefer "shipped" over "released" or "launched"
- keep under 220 characters when possible
```

At onboarding you can optionally paste 3–5 of your existing posts to seed the profile, or skip and let it learn purely from edits — your choice.

---

## Batching / digest

Not every commit deserves its own post. Small or trivial commits drop into an **unposted backlog** instead of being ignored forever.

When you click **"Wrap up my day"** on the dashboard, Shiplog reads all backlog diffs together and generates **one themed post** — e.g. *"spent today hardening the auth layer — fixed token expiry edge case, tightened input validation, cleaned up middleware →"*

**Rollout phases:**
- **Phase 1 (now):** single-commit pipeline only
- **Phase 2:** backlog + manual "wrap up my day" button
- **Phase 3:** automatic end-of-day trigger once grouping is trusted

---

## Design decisions

A few non-obvious choices baked into the architecture:

- **No auto-posting to X or LinkedIn.** X's free API tier is discontinued; posts with links cost ~$0.20 each. LinkedIn's publishing API requires Partner Program approval. Both platforms use copy-to-clipboard + composer deep-links instead — $0 cost, full editorial control.
- **dev.to is the exception** — it has a clean public API that supports pushing real drafts (`published: false`). Shiplog pushes directly; you review and publish on dev.to.
- **README updates are free and automatic** — committed to your repo via the GitHub API on approval. Shiplog only touches the specific section affected by the change, never the whole file.
- **Idempotent by commit SHA** — Shiplog never generates or posts content for a commit it already handled.
- **Single-user V1, multi-user-ready architecture** — Postgres, per-user rows, and login are in from day one so multi-user support is an extension, not a rewrite.

---

## Roadmap

- [ ] Database wiring (Neon + Alembic migration)
- [ ] Stage 3: diff enrichment via GitHub API
- [ ] Stage 4: LLM classifier (trivial / medium / milestone)
- [ ] Stage 5: generator (X, LinkedIn, dev.to, README)
- [ ] Stage 6: review feed dashboard (React + Tailwind)
- [ ] Stage 7: one-click copy + dev.to draft push + README commit
- [ ] Stage 8: history log
- [ ] Learning loop: style profile + confirm-before-save
- [ ] Batching: backlog + "wrap up my day" button
- [ ] Multi-user: OAuth, per-user token storage, data isolation

---

## License

MIT
