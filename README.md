# EduMitra AI

**Team:** CodyRhodes · **Live:** https://edumitraai.vercel.app

An AI tutor and wellness companion for Indian students grades 6–12. NCERT-aligned, works in 11 Indian languages, compliant with DPDP Act 2023.


---

## Overview

EduMitra addresses two intersecting challenges faced by 250 million Indian students: rigid one-size-fits-all content delivery and fragmented mental wellness support. The platform uses a LangGraph-powered supervisor orchestrating six specialized AI agents, each with independent model fallbacks, circuit breakers, and guardrails.

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                 │
│  Dark glassmorphism · Voice mode · Real-time chat       │
│  Progress dashboards · Wellness check-ins               │
└─────────────────────┬───────────────────────────────────┘
                      │ REST / Auth
┌─────────────────────▼───────────────────────────────────┐
│                Backend (FastAPI · Python 3.12)            │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐  │
│  │ Auth     │ │ Study    │ │Wellness│ │ Data         │  │
│  │ + JWT    │ │ Chat/Quiz│ │Check-in│ │ Protection   │  │
│  └──────────┘ └──────────┘ └────────┘ └──────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              LangGraph Agent Supervisor                  │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐  │
│  │Curriculum│ │ Content  │ │Wellness│ │ Bhasha Voice │  │
│  │ RAG      │ │ Generator│ │ Agent  │ │ (11 langs)   │  │
│  └──────────┘ └──────────┘ └────────┘ └──────────────┘  │
│  ┌──────────┐ ┌──────────┐                               │
│  │ Progress │ │Multimodal│                               │
│  │ Tracker  │ │ Vision   │                               │
│  └──────────┘ └──────────┘                               │
│  Circuit breaker · Sanitizer · Output guardrail          │
└─────────────────────────────────────────────────────────┘
```

## Key Features

- **Multi-Agent Architecture** — LangGraph supervisor with 6 specialized agents: curriculum RAG, content generation, voice (11 Indian languages), wellness check-in, progress tracking, and multimodal vision analysis. Each agent has independent fallback chains and circuit breakers.
- **NCERT-Aligned RAG** — ChromaDB vector store seeded with NCERT textbook content across 5 subjects. Every answer is grounded in curriculum material, not generic web data.
- **Wellness Companion** — Deterministic crisis classifier with Indian helpline numbers (iCall, Vandrevala, KIRAN, AASRA, Childline). No AI diagnosis or prescriptions — the LLM never touches mental health decisions.
- **Voice in 11 Languages** — Browser-native Web Speech API with Sarvam AI fallback. Works offline for STT. No server-side transcription cost.
- **Prompt Injection Defense** — Every user input passes through a sanitizer before reaching any LLM. Output guardrails enforce content safety. Circuit breaker prevents runaway API costs.
- **DPDP Act 2023 Compliant** — Right to erasure, data portability export, encryption at rest, parental consent gate for minors, retention policy disclosure. Built from day one, not retrofitted.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, Material UI |
| Backend | FastAPI, Python 3.12, async throughout |
| LLM | Groq (Llama 3.3 70B) via OpenAI-compatible SDK |
| Voice | Web Speech API + Sarvam AI (fallback) |
| Vector Store | ChromaDB (all-MiniLM-L6-v2 embeddings) |
| Agent Framework | LangGraph with circuit breaker, sanitizer, guardrails |
| Auth | JWT-based, bcrypt password hashing |
| Security | Prompt injection sanitizer, output guardrail, rate limiting, CORS |
| Deploy | Render (backend), Vercel (frontend) |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/auth/signup` | User registration |
| `POST` | `/api/auth/signin` | User login |
| `POST` | `/api/study/query` | Chat with AI tutor |
| `POST` | `/api/study/quiz` | Generate quiz |
| `GET` | `/api/study/plan` | Generate study plan |
| `POST` | `/api/study/voice` | Upload audio for STT + response |
| `POST` | `/api/generate/image` | Generate image |
| `POST` | `/api/upload` | Upload for vision analysis |
| `POST` | `/api/wellness/checkin` | Wellness check-in |
| `GET` | `/api/wellness/history` | Wellness history |
| `GET` | `/api/progress` | Study progress |
| `GET` | `/api/progress/burnout-risk` | Burnout risk assessment |
| `GET` | `/api/dashboard` | Student dashboard |
| `GET` | `/api/teacher/students` | Teacher dashboard |
| `GET` | `/api/parent/child-progress` | Parent dashboard |
| `DELETE` | `/api/data/me` | Right to erasure (DPDP Act) |
| `GET` | `/api/data/export` | Data portability export |
| `GET` | `/api/data/retention-policy` | Retention policy |

## Quick Start

### Prerequisites

- Python 3.12+, Node.js 18+
- API keys: Groq (`gsk_*`), Supabase, Sarvam AI (for voice)

### Backend

```bash
cd backend
python -m venv venv && venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Set GROK_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_ANON_KEY, ENCRYPTION_KEY in .env
uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # Fill NEXT_PUBLIC_API_URL, SUPABASE vars
npm run dev
```

### Testing

```bash
pytest tests/ -v
```

## Architecture Decisions

- **No single point of LLM failure** — Every agent has a fallback chain. If Groq rate-limits, the circuit breaker opens and the system degrades gracefully.
- **Wellness is non-AI** — The crisis classifier uses deterministic keyword matching. Helpline numbers are hardcoded and verified. The LLM is explicitly excluded from all mental health decisions.
- **RAG over NCERT, not web** — Answers stay syllabus-aligned by grounding generation in retrieved curriculum chunks (0.65 relevance threshold).
- **Browser-side STT** — Voice transcription costs zero server-side. The Sarvam AI API is a fallback, not the primary path.
- **DPDP Act from day one** — Erasure, export, encryption, consent, and retention are platform features, not afterthoughts.

## Security

- All user inputs sanitized before reaching any LLM
- Output guardrail enforces content safety
- Rate limiting per IP (100 req/min)
- CORS restricted to known frontend origins
- Wellness/sentiment data encrypted at rest with strictest RLS
- JWT-based authentication with bcrypt password hashing
- `.env` and secrets never committed to repository

## License

Apache 2.0
