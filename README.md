# ServiceNow AI Demo

An AI-powered guidance tool for IT support specialists. A specialist describes the symptoms of an open ticket in plain language — the system searches your team's history of past resolved tickets and generates a step-by-step resolution playbook using Claude Haiku.

**This is not a ticketing system.** The ticket already exists in ServiceNow, Jira, or whatever the real system is. This is the knowledge layer on top of it.

---

## What It Does

### Guidance Search
Specialist describes the issue they are working on. The system retrieves all past resolved tickets from the knowledge base and sends them to Claude Haiku as context. Claude identifies which past cases are relevant and synthesizes a unified playbook — likely root cause, confidence level, numbered steps, escalation path if needed, and warnings. The specific tickets it referenced are shown below so the specialist can verify the reasoning.

### Ticket Lifecycle Demo
Full incident lifecycle: create ticket → AI classifies and routes it → specialist works it → work notes logged → sub-ticket opened for another team if needed → resolved with documented steps → resolution enters knowledge base automatically.

### AI Ticket Classifier
Describe a new issue, Claude suggests: category, priority (P1–P4 with reasoning), and which team to route it to (with reasoning). Pre-fills the ticket creation form.

### Analytics
- AI guidance helpful rate (thumbs up/down feedback)
- Escalation rate (tickets requiring sub-tickets)
- Ticket volume by category
- Average resolution time by priority
- Knowledge gap detection — surfaces recent searches where the AI had low confidence and found no matching tickets

### SLA Tracking
Color-coded SLA timer on every ticket. P1=1h, P2=4h, P3=8h, P4=24h. Major incident banner fires when 3+ open tickets appear in the same category within one hour.

---

## Tech Stack

| | |
|---|---|
| Backend | FastAPI + Uvicorn |
| Database | SQLite via SQLAlchemy 1.4 |
| AI | Claude Haiku (`claude-haiku-4-5-20251001`) via Anthropic SDK |
| Frontend | Jinja2 templates + Tailwind CSS (CDN) |
| Pattern | RAG — Retrieval-Augmented Generation |

---

## Setup

**1. Clone and install dependencies**
```bash
pip install -r requirements.txt
```

**2. Set your API key**
```bash
cp .env.example .env
```
Open `.env` and replace `your_key_here` with your Anthropic API key. Get one at [console.anthropic.com](https://console.anthropic.com).

**3. Run**
```bash
python run.py
```

The app starts at [http://localhost:8000](http://localhost:8000). The database is created and seeded automatically on first run — 46 realistic IT support tickets across 6 categories with full resolution notes and work note timelines.

---

## Project Structure

```
app/
├── main.py                  # FastAPI app, router registration, startup hooks
├── config.py                # API key, model name, database URL
├── database/
│   ├── models.py            # SQLAlchemy models: Ticket, Team, WorkNote, GuidanceFeedback, SearchLog
│   ├── db.py                # Engine, session, init_db()
│   ├── seed.py              # 46 seeded tickets + work notes
│   └── migrations.py        # SQLite ALTER TABLE guards for schema changes
├── routers/
│   ├── search.py            # GET / and POST /search (guidance search + search logging)
│   ├── tickets.py           # Dashboard, ticket detail, create, analyze, sub-ticket
│   ├── work_notes.py        # Add work note, change status (with resolution capture)
│   ├── feedback.py          # POST /feedback/ (thumbs up/down)
│   ├── analytics.py         # GET /analytics
│   └── demo.py              # GET /demo (How It Works)
├── services/
│   ├── ai_service.py        # get_specialist_guidance, suggest_next_action, classify_new_ticket
│   ├── ticket_service.py    # All DB operations for tickets and work notes
│   ├── sla_service.py       # SLA timer calculation, major incident detection
│   └── analytics_service.py # Feedback stats, escalation rate, knowledge gaps
└── templates/               # Jinja2 HTML templates (Tailwind CSS)
```

---

## How the AI Works (RAG Pattern)

Every time a specialist runs a search:

1. All resolved tickets are pulled from the SQLite database
2. Each ticket's title, category, resolution, and resolution notes are formatted as context
3. That context — along with the specialist's description — is sent to Claude Haiku in a single prompt
4. Claude reads the full history, identifies which past cases are relevant, and writes a unified guidance playbook as structured JSON
5. The app parses the JSON and renders the results page

The AI model itself is never retrained. But as more tickets are resolved with detailed notes, the retrieval pool grows — so future guidance draws from more real examples and becomes more specific.

---

## Key Business Rules the AI Enforces

These are embedded directly in the resolution notes of relevant seeded tickets, so Claude surfaces them whenever a similar issue comes up:

- **Manager approval required before granting any permissions** — the AI will always flag this on access and entitlement tickets
- **Sub-tickets for third-party systems** — when another team needs to act (Fund Services, Network, Vendor), the AI specifies exactly what system to open a ticket in and what information to include
- **Never disable SSL verification** as a workaround — explicitly warned against even under pressure
- **Secure credential delivery only** — API keys always via secure channel, never plain email or chat
- **P1 escalation** — multiple teams blocked = P1, AI flags immediately

---

## Example Queries to Try

- `User can log into Salesforce but cannot edit records — coworker with the same role can edit fine`
- `Client API key stopped working overnight with a 401 error — no code changes were made`
- `Access Denied on vendor portal when VPN is connected, works fine without VPN — multiple users affected`
- `User cannot see the Reporting module after last weekend's system update`
- `SSL certificate error on internal API endpoint — multiple teams affected since Monday`
- `Fund Services portal shows Access Denied — manager and teammates can log in fine`
- `User plugged in an unknown USB drive and endpoint protection is alerting`
