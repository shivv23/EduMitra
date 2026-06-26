# EduMitra AI

**Team:** shivamkumar0423 · **Live:** https://edumitraai.vercel.app

An AI tutor and wellness companion for Indian students grades 6–12. NCERT-aligned, works in 11 Indian languages, compliant with DPDP Act 2023.

[▶ Watch Demo](https://drive.google.com/file/d/1trRTSuqPH0p0drXjT9qoKJlzKxEQfaUk/view?usp=sharing)

---

## Overview

```
frontend/          — Next.js 14 (App Router), Tailwind, TypeScript
backend/           — FastAPI (Python 3.12), Supabase, httpx
agents/            — LangGraph supervisor + specialized agents
├── langgraph/     — Graph orchestration, sanitizer, circuit breaker, guardrails
├── content_gen/   — Explanations, quizzes, mind maps, image gen (Stable Diffusion)
├── rag/           — ChromaDB vector store + curriculum retrieval
├── bhasha/        — Sarvam AI STT/TTS for 11 Indian languages
├── wellness/      — Crisis classifier + check-in processing
├── progress/      — Mastery tracking, burnout risk, alert dispatch
└── multimodal/    — Image upload validation + vision analysis
```

## What makes it different

Most edtech platforms do one thing: serve content. EduMitra connects learning with wellness in a single flow. The architecture uses multiple specialized AI agents instead of one monolithic model — each agent has its own model, prompt, and fallback chain. If Claude rate-limits, Gemini takes over. There's no single point of LLM failure.

The wellness agent never uses AI for diagnosis or prescriptions. It runs a deterministic keyword classifier to detect crisis signals and shows helpline numbers. The LLM never touches mental health decisions.

Voice works in 11 Indian languages through the browser's Web Speech API (free, works offline) with Sarvam AI as a backend fallback. No dependency on English.

Every user input goes through a prompt injection sanitizer before reaching any LLM — not just a system prompt, actual sanitization logic.

## What's built

**Frontend** — Next.js 14 App Router, TypeScript, Tailwind. 9 routes, 16 components. Deployed on Vercel. Dark glassmorphism theme with gradient accents. Every button has hover and active feedback. Loading and error states on every data fetch with retry buttons. Voice mode with language selector built into the study page. Real Indian helpline numbers (iCall, Vandrevala, KIRAN, AASRA, Childline) displayed in the wellness section.

**Backend** — FastAPI, 18 REST endpoints, async throughout. Deployed on Railway via Docker. Supabase SSR auth with email/password. Middleware guards every protected route. JWT forwarded from frontend to backend for authenticated API calls.

**RAG pipeline** — ChromaDB vector store with all-MiniLM-L6-v2 embeddings. 29+ NCERT chunks seeded across 5 subjects. 0.65 relevance threshold. Retrieval happens before every LLM call to ground answers in curriculum content.

**Agent orchestration** — LangGraph supervisor with circuit breaker (3 failures opens the circuit, 30-second timeout per node). 6 agent types: curriculum RAG, content generation, voice, wellness, progress tracking, multimodal. Each wrapped with timeout and retry logic.

**Tests** — 15 test files covering sanitizer, circuit breaker, crisis detection, XSS, RAG ingestion, file upload validation, webhook security, RLS isolation, encryption, and red-team testing.

**CI/CD** — GitHub Actions (lint → test → build). Dependabot for pip and npm. Pre-commit hooks (gitleaks, bandit, ruff, trailing whitespace, YAML/JSON validation).

## The problem it solves

250 million Indian students across CBSE and state board curricula. No personalized learning adaptation — every student gets the same content regardless of their pace or gaps. 53% of Indian students report anxiety, but wellness support lives in completely separate apps (if it exists at all). Most platforms treat DPDP Act compliance as an afterthought.

EduMitra uses RAG over NCERT textbooks, not generic web data, so answers stay syllabus-aligned. Quiz performance feeds back into content selection — weak areas get more practice, strong areas move faster. Wellness is part of the same flow, not a separate app. A student checks their mood, gets immediate support if needed, and goes back to studying.

DPDP Act compliance was built in from the start — erasure endpoint, data export, encryption at rest, parental consent gate for minors.

## Scale and cost

The backend is stateless — every agent is a stateless function. Scale horizontally behind a load balancer. ChromaDB is persistent and local, no cloud vector DB dependency, no per-query cost. Browser-side STT means zero server cost for voice transcription — the Sarvam API only runs as a fallback. Claude is the primary LLM for content quality, Gemini handles fallback when cost matters. The circuit breaker prevents runaway API calls from a single buggy request.

250 million addressable users. No per-user infrastructure cost beyond a database row. RAG scales with index size, not user count.

---

## Quick Start

### Prerequisites
- Python 3.12+, Node.js 18+
- Supabase project (free tier works)
- API keys: Gemini, Claude, Sarvam AI, Stability AI, LangChain

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp ../.env.example ../.env  # Fill in your keys
uvicorn src.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### API Keys Required

| Key | Source | Used By |
|-----|--------|---------|
| `GEMINI_API_KEY` | aistudio.google.com | Chat, content generation |
| `CLAUDE_API_KEY` | console.anthropic.com | Content generation (primary) |
| `SARVAM_API_KEY` | dashboard.sarvam.ai | Voice STT/TTS in 11 Indian languages |
| `STABLE_DIFFUSION_API_KEY` | platform.stability.ai | Image generation |
| `LANGCHAIN_API_KEY` | smith.langchain.com | LangSmith tracing |
| `SUPABASE_*` | supabase.com | Database, auth, storage |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/study/query` | Chat with AI tutor |
| `POST` | `/api/langgraph/query` | Full LangGraph supervisor pipeline |
| `POST` | `/api/study/quiz` | Generate quiz |
| `GET` | `/api/study/plan` | Generate study plan |
| `POST` | `/api/study/voice` | Upload audio for STT + AI response |
| `POST` | `/api/generate/image` | Generate image via Stable Diffusion |
| `POST` | `/api/upload` | Upload image for vision analysis |
| `POST` | `/api/wellness/checkin` | Wellness check-in |
| `GET` | `/api/wellness/history` | Wellness history |
| `GET` | `/api/progress` | Study progress |
| `GET` | `/api/progress/burnout-risk` | Burnout risk assessment |
| `GET` | `/api/dashboard` | Student dashboard |
| `GET` | `/api/teacher/students` | Teacher view of students |
| `GET` | `/api/parent/child-progress` | Parent view of child progress |
| `DELETE` | `/api/data/me` | Right to erasure (DPDP Act) |
| `GET` | `/api/data/export` | Data portability export |
| `GET` | `/api/data/retention-policy` | Data retention policy |

## Testing

```bash
pytest tests/ -v
```

## License

Apache 2.0
