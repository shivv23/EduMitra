-- EduMitra AI: Row Level Security Policies
-- Run this entire file in Supabase SQL Editor

-- ============================================================
-- STEP 1: CREATE ALL TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'parent', 'teacher', 'admin')),
    name_encrypted BYTEA,
    phone_hash TEXT UNIQUE,
    email_encrypted BYTEA,
    school_encrypted BYTEA,
    grade INTEGER CHECK (grade >= 1 AND grade <= 12),
    preferred_language TEXT DEFAULT 'en',
    parental_consent BOOLEAN DEFAULT FALSE,
    consent_granted_at TIMESTAMPTZ,
    data_retention_days INTEGER DEFAULT 365,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.study_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    mastery_score REAL DEFAULT 0.0,
    quizzes_taken INTEGER DEFAULT 0,
    quizzes_passed INTEGER DEFAULT 0,
    study_plan JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.wellness_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    sentiment_score REAL,
    check_in_response_encrypted BYTEA,
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    crisis_detected BOOLEAN DEFAULT FALSE,
    escalation_triggered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    retention_date TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '90 days')
);

CREATE TABLE IF NOT EXISTS public.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL CHECK (alert_type IN ('wellness', 'academic', 'burnout_risk')),
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    dispatched_to JSONB,
    human_in_loop BOOLEAN DEFAULT FALSE,
    alert_content_encrypted BYTEA,
    audit_log JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS public.parent_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(parent_id, student_id)
);

CREATE TABLE IF NOT EXISTS public.teacher_students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    subject TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(teacher_id, student_id)
);

CREATE TABLE IF NOT EXISTS public.session_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    session_summary_encrypted BYTEA,
    mastery_snapshot JSONB,
    topics_reviewed TEXT[],
    wellness_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- STEP 2: ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- ============================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wellness_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.parent_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.teacher_students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.session_memory ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 3: CREATE ALL POLICIES
-- ============================================================

-- ── Profiles ──────────────────────────────────────────────
CREATE POLICY "profiles_self_access" ON public.profiles
    FOR ALL
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY "profiles_parent_access" ON public.profiles
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_links
            WHERE parent_links.student_id = profiles.id
            AND parent_links.parent_id = auth.uid()
            AND parent_links.verified = TRUE
        )
    );

CREATE POLICY "profiles_teacher_access" ON public.profiles
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.teacher_students
            WHERE teacher_students.student_id = profiles.id
            AND teacher_students.teacher_id = auth.uid()
        )
    );

CREATE POLICY "profiles_admin_read" ON public.profiles
    FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

-- ── Study Progress ──────────────────────────────────────
CREATE POLICY "study_progress_self" ON public.study_progress
    FOR ALL
    USING (student_id = auth.uid())
    WITH CHECK (student_id = auth.uid());

CREATE POLICY "study_progress_teacher" ON public.study_progress
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.teacher_students
            WHERE teacher_students.student_id = study_progress.student_id
            AND teacher_students.teacher_id = auth.uid()
        )
    );

-- ── Wellness Data (highest sensitivity) ─────────────────
CREATE POLICY "wellness_data_self" ON public.wellness_data
    FOR SELECT
    USING (student_id = auth.uid());

CREATE POLICY "wellness_data_insert_self" ON public.wellness_data
    FOR INSERT
    WITH CHECK (student_id = auth.uid());

-- ── Alerts ──────────────────────────────────────────────
CREATE POLICY "alerts_self_read" ON public.alerts
    FOR SELECT
    USING (student_id = auth.uid());

CREATE POLICY "alerts_teacher_read" ON public.alerts
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.teacher_students
            WHERE teacher_students.student_id = alerts.student_id
            AND teacher_students.teacher_id = auth.uid()
        )
    );

-- ── Parent Links ────────────────────────────────────────
CREATE POLICY "parent_links_self" ON public.parent_links
    FOR SELECT
    USING (parent_id = auth.uid() OR student_id = auth.uid());

-- ── Teacher Students ─────────────────────────────────────
CREATE POLICY "teacher_students_self" ON public.teacher_students
    FOR SELECT
    USING (teacher_id = auth.uid() OR student_id = auth.uid());

-- ── Session Memory ──────────────────────────────────────
CREATE POLICY "session_memory_self" ON public.session_memory
    FOR ALL
    USING (student_id = auth.uid())
    WITH CHECK (student_id = auth.uid());

-- ============================================================
-- STEP 4: INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_phone_hash ON public.profiles(phone_hash);
CREATE INDEX IF NOT EXISTS idx_study_progress_student ON public.study_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_wellness_data_student ON public.wellness_data(student_id);
CREATE INDEX IF NOT EXISTS idx_wellness_data_crisis ON public.wellness_data(crisis_detected) WHERE crisis_detected = TRUE;
CREATE INDEX IF NOT EXISTS idx_alerts_student ON public.alerts(student_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON public.alerts(severity) WHERE severity IN ('high', 'critical');
CREATE INDEX IF NOT EXISTS idx_session_memory_student ON public.session_memory(student_id);
