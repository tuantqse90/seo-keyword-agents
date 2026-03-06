# SEO Dashboard

Full-stack SEO intelligence platform with real-time AI analysis streaming. Built with Next.js 14, FastAPI, and PostgreSQL.

## Features

- **4 SEO Modules** — Keyword Research, Competitor Analysis, Content Brief, On-Page Audit
- **3 Combined Workflows** — Full Report, Strategy, Quick Fix
- **Real-time Streaming** — SSE streaming of AI analysis results
- **Dual LLM Support** — Anthropic Claude + DeepSeek
- **Vietnamese UI** — Full Vietnamese interface
- **Dark Mode** — Toggle with persistence
- **Mobile Responsive** — Collapsible sidebar, adaptive layouts
- **JWT Authentication** — Register/login with bcrypt password hashing
- **Scheduled Analysis** — Cron-like recurring SEO audits with email notifications
- **Report Comparison** — Side-by-side report diff view
- **Full-text Search** — Search across all reports (Ctrl+K)
- **Dashboard Charts** — Recharts-powered analytics (bar + pie charts)
- **CSV/PDF Export** — Download reports in multiple formats
- **Error Recovery** — Auto-recover stuck reports on server restart + retry UI

## Architecture

```
Browser (Next.js 14 + Tailwind CSS)
    |  HTTP / SSE
FastAPI Backend (Python 3.11+)
    |  Anthropic SDK / OpenAI SDK
LLM API (Claude / DeepSeek)
    |
PostgreSQL 16 (10 tables)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), Tailwind CSS, Recharts, react-markdown |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic |
| AI | Anthropic SDK, OpenAI SDK (DeepSeek-compatible) |
| Database | PostgreSQL 16, asyncpg |
| Auth | JWT (PyJWT), bcrypt (passlib) |
| Export | weasyprint (PDF), csv module |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16

### 1. Clone & Setup

```bash
git clone https://github.com/tuantqse90/seo-keyword-agents.git
cd seo-keyword-agents
cp .env.example .env
```

### 2. Configure `.env`

```env
DATABASE_URL=postgresql+asyncpg://seo_user:seo_password@localhost:5432/seo_dashboard

# Choose your LLM provider
LLM_PROVIDER=deepseek          # or "anthropic"
DEEPSEEK_API_KEY=sk-xxxxx      # if using DeepSeek
ANTHROPIC_API_KEY=sk-ant-xxxxx # if using Anthropic

JWT_SECRET=your-secret-key-here
```

### 3. Database Setup

```bash
# Option A: Docker
docker compose up -d

# Option B: Local PostgreSQL
createuser seo_user
createdb -O seo_user seo_dashboard
```

### 4. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** — register an account and start analyzing!

## Project Structure

```
seo-keyword-agents/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry + lifespan
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy async engine
│   │   ├── models/              # 10 SQLAlchemy models
│   │   │   ├── report.py        # Reports (core)
│   │   │   ├── keyword.py       # Keywords with clusters
│   │   │   ├── competitor.py    # Competitors + keyword gaps
│   │   │   ├── content_brief.py # Content briefs
│   │   │   ├── audit.py         # Audit results + issues
│   │   │   ├── project.py       # Projects
│   │   │   ├── schedule.py      # Scheduled analyses
│   │   │   └── user.py          # User auth
│   │   ├── routers/             # 9 API routers
│   │   │   ├── keywords.py      # POST /analyze + SSE stream
│   │   │   ├── competitor.py
│   │   │   ├── content.py
│   │   │   ├── audit.py
│   │   │   ├── workflows.py     # Combined workflows
│   │   │   ├── reports.py       # CRUD + stats + search + export
│   │   │   ├── schedules.py     # Schedule CRUD
│   │   │   ├── auth.py          # Register/login/me
│   │   │   └── projects.py      # Project CRUD
│   │   └── services/
│   │       ├── claude_client.py  # Dual LLM streaming client
│   │       ├── prompt_builder.py # Module-specific prompts
│   │       ├── parser.py         # JSON + markdown table parser
│   │       ├── *_service.py      # Module persistence services
│   │       ├── auth_service.py   # JWT + bcrypt
│   │       ├── scheduler_service.py # Background task scheduler
│   │       ├── email_service.py  # SMTP notifications
│   │       └── export_service.py # CSV + PDF export
│   ├── alembic/                  # Database migrations
│   └── tests/                    # 60 pytest tests
│
├── frontend/
│   ├── src/
│   │   ├── app/                  # 14 Next.js pages
│   │   │   ├── page.tsx          # Dashboard with charts
│   │   │   ├── keywords/         # Keyword research
│   │   │   ├── competitor/       # Competitor analysis
│   │   │   ├── content/          # Content brief
│   │   │   ├── audit/            # SEO audit
│   │   │   ├── full/             # Full workflow
│   │   │   ├── strategy/         # Strategy workflow
│   │   │   ├── fix/              # Fix workflow
│   │   │   ├── reports/          # Reports list + detail
│   │   │   ├── compare/          # Side-by-side comparison
│   │   │   ├── schedules/        # Schedule management
│   │   │   └── login/            # Auth page
│   │   ├── components/           # 20+ React components
│   │   ├── hooks/                # useSSE, useAuth, useTheme, useApi
│   │   ├── lib/                  # API client, types, constants
│   │   └── i18n/vi.ts            # Vietnamese strings
│   └── tailwind.config.ts
│
├── docker-compose.yml            # PostgreSQL container
├── seo-agent-prompt.txt          # System prompt (source of truth)
└── .env.example                  # Environment template
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{module}/analyze` | Start analysis (returns report_id + stream_url) |
| GET | `/api/{module}/stream/{id}` | SSE stream of AI response |
| GET | `/api/{module}/{id}` | Get structured results |
| POST | `/api/workflows/{type}` | Start combined workflow |
| GET | `/api/reports` | List reports (filterable) |
| GET | `/api/reports/stats` | Dashboard statistics |
| GET | `/api/reports/search?q=` | Full-text search |
| GET | `/api/reports/{id}/export/{csv\|pdf}` | Export report |
| POST | `/api/reports/{id}/retry` | Retry failed report |
| CRUD | `/api/schedules` | Manage scheduled analyses |
| CRUD | `/api/projects` | Manage projects |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user |

## SEO Modules

### Keyword Research (`/keywords`)
- 15-20 keyword suggestions with clusters
- Search volume, difficulty, intent, CPC, opportunity score
- Golden keywords highlighted (high volume + low difficulty)

### Competitor Analysis (`/competitor`)
- 3-5 competitor profiles with traffic and DA
- Keyword gap matrix
- Strengths/weaknesses analysis

### Content Brief (`/content`)
- Title tag + meta description (optimized length)
- Full H2/H3 outline with key points
- LSI keywords, snippet strategy, E-E-A-T signals

### On-Page Audit (`/audit`)
- SEO score (0-100) with letter grade
- Issues by severity (Critical/Warning/Info)
- Quick wins with effort level tags
- Technical checklist

## Testing

```bash
cd backend
pytest tests/ -v    # 60 tests
```

## Email Notifications (Optional)

Configure SMTP in `.env` to receive email alerts when scheduled analyses complete:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=app-password
NOTIFY_EMAIL=your@gmail.com
```

## License

MIT
