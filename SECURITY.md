# EduMitra AI — Security Threat Model

## 1. Prompt Injection

**Risk**: User-supplied text, transcribed audio, or retrieved document chunks may contain
instructions that override system prompts, causing the LLM to ignore guardrails, leak data,
or generate harmful content.

**Mitigations**:
- All untrusted input passes through a sanitization layer before reaching any LLM.
- User content is wrapped in `<untrusted>...</untrusted>` delimiters in prompts.
- System prompt explicitly instructs the model to treat user content as data, not instructions.
- Retrieved RAG chunks are tagged as untrusted in the prompt template.
- Output guardrails scan LLM responses for leaked system prompts or PII.

## 2. PII Leakage (Minors' Data)

**Risk**: EduMitra AI processes data from minors (K-12 students). Exposure of names, phone
numbers, location, school details, or emotional state violates India's DPDP Act 2023 and
causes severe reputational/legal harm.

**Mitigations**:
- PII fields (name, phone, school) encrypted at rest using application-level Fernet encryption.
- Phone numbers stored as hashed values only for lookup.
- Row Level Security (RLS) ensures a student can ONLY access their own records.
- Structured logging explicitly redacts PII, raw messages, and tokens.
- Wellness/sentiment data encrypted at rest with strictest access controls, excluded from
  analytics exports unless explicitly consented and anonymized.
- Data retention and right-to-erasure endpoints implemented.

## 3. API Key Exposure

**Risk**: Leaked Gemini, Claude, Sarvam AI, Supabase, or WhatsApp API keys can lead to
financial loss, service abuse, and data breaches.

**Mitigations**:
- All secrets loaded from environment variables ONLY via pydantic-settings.
- .env is in .gitignore; .env.example contains placeholders only.
- Pre-commit hook gitleaks scans for secrets before every commit.
- CI pipeline runs gitleaks + bandit + pip-audit on every PR.
- Frontend bundle contains only the Supabase anon key; all privileged calls go through backend.

## 4. SSRF via Image URLs

**Risk**: If the system accepts external URLs for image/vision processing, an attacker could
make the server request internal services (e.g., cloud metadata endpoints) or malicious hosts.

**Mitigations**:
- The system NEVER passes user-supplied URLs to the vision API.
- Only validated, server-stored objects (after re-encode + randomized naming) are passed to
  vision models.
- File uploads are restricted by magic-byte validation, max size, and re-encoding.

## 5. Insecure File Uploads

**Risk**: Malicious file uploads (polyglot files, embedded payloads, EXIF with GPS data, malware)
can compromise the server and leak student location data.

**Mitigations**:
- MIME type enforced by magic bytes (not extension or Content-Type).
- Files re-encoded/transcoded server-side via Pillow to strip embedded payloads and EXIF.
- Max file size and dimension limits enforced.
- Randomized, non-guessable filenames in private storage bucket.
- Files served via signed, expiring URLs — never from the upload path directly.

## 6. Wellness Agent Liability

**Risk**: The Wellness Agent interacts with potentially distressed minors. Improper responses
could delay critical care or cause harm.

**Mitigations**:
- Deterministic crisis classifier detects self-harm/suicidal signals before any generative response.
- On detection: returns pre-approved safe response with verified India helpline numbers (not
  LLM-invented numbers) and triggers escalation.
- Agent never diagnoses, prescribes, or claims to be a medical professional (enforced via
  system prompt + output guardrail).
- Age-appropriate disclaimers on all wellness interactions.
- Human clinical review required before any real deployment.
- Sentiment data encrypted at rest, strictest RLS, minimal retention.

## 7. Authentication & Authorization Bypass

**Risk**: Unauthorized access to student data, privilege escalation, or session hijacking.

**Mitigations**:
- JWT verified against Supabase JWKS on EVERY protected route.
- Client-supplied user IDs never trusted; user identity derived from verified JWT.
- RBAC with roles: student, parent, teacher, admin — enforced as FastAPI dependency.
- RLS policies at the database level as defense-in-depth.
- CSRF protection with SameSite cookies on state-changing requests.

## 8. Webhook Security (WhatsApp)

**Risk**: WhatsApp webhooks receive messages from arbitrary sources. Spoofed payloads,
replay attacks, or signature bypass could lead to abuse.

**Mitigations**:
- HMAC signature verification (X-Hub-Signature-256) with constant-time comparison.
- Idempotency store prevents replay/double-processing.
- Schema validation on every inbound payload.
- Rate-limited per phone number.

## 9. Supply Chain

**Risk**: Compromised dependencies could introduce vulnerabilities.

**Mitigations**:
- pip-audit / safety scans in CI.
- npm audit for frontend.
- Dependabot configured for automated updates.
- Dependency pinning with lockfiles.

## 10. Data Exfiltration via LLM

**Risk**: LLM could be manipulated to output training data or system prompts.

**Mitigations**:
- Output guardrail node in LangGraph scans all agent outputs before returning to user.
- Bounded conversation history prevents context stuffing.
- No eval/exec/shell access from any agent.
- Structured output schemas enforced via Pydantic validation.

---

*Last updated: June 2026*
*Review cycle: Every sprint or upon dependency/API change*
