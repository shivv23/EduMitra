const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://edumitra-ai.onrender.com";

let _authToken: string | null = null;

export function setAuthToken(token: string | null) {
  _authToken = token;
  if (typeof document !== "undefined") {
    if (token) {
      document.cookie = `edumitra_token=${token}; path=/; max-age=2592000; SameSite=Lax`;
    } else {
      document.cookie = "edumitra_token=; path=/; max-age=0";
    }
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string>),
  };
  if (_authToken) {
    headers["Authorization"] = `Bearer ${_authToken}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    signal: AbortSignal.timeout(60000),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }

  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  upload: <T>(path: string, formData: FormData) => {
    const headers: Record<string, string> = {};
    if (_authToken) headers["Authorization"] = `Bearer ${_authToken}`;
    return fetch(`${API_BASE}${path}`, {
      method: "POST",
      body: formData,
      headers,
      signal: AbortSignal.timeout(60000),
    }).then(async (res) => {
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      return res.json() as T;
    });
  },
};

export async function fetchDashboard() {
  return api.get<{
    overall_mastery: number;
    topics_covered: number;
    quizzes_taken: number;
    streak: number;
    wellness_status: string;
    last_checkin?: string;
  }>("/api/dashboard");
}

export async function fetchStudyPlan() {
  return api.get<{
    days: { day: number; title: string; focus: string; estimated_minutes: number; completed: boolean }[];
  }>("/api/study/plan");
}

export async function fetchQuiz(topic?: string) {
  return api.post<{
    questions: { question: string; options: string[]; correctAnswer: number; explanation: string }[];
  }>("/api/study/quiz", { topic: topic || "quadratic_equations" });
}

export async function sendChatMessage(message: string, history?: { role: string; content: string }[]) {
  return api.post<{ response: string; type: string }>("/api/study/query", {
    message,
    history: history || [],
  });
}

export async function uploadNotes(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return api.upload<{ analysis: string; summary: string }>("/api/study/query/file", formData);
}

export async function wellnessCheckIn(sentiment: number, note?: string) {
  return api.post<{ response: string; risk_level: string; crisis_detected: boolean }>(
    "/api/wellness/checkin",
    { sentiment_score: sentiment, note }
  );
}

export async function fetchWellnessHistory() {
  return api.get<{ checkins: { sentiment_score: number; created_at: string }[] }>(
    "/api/wellness/history"
  );
}

export async function fetchProgress() {
  return api.get<{
    overall_mastery: number;
    subjects: { name: string; mastery: number; trend: string }[];
    recent_activity: { action: string; detail: string; time: string }[];
    streak: number;
    quizzes_taken: number;
    topics_covered: number;
  }>("/api/progress");
}

export async function fetchStudents() {
  return api.get<{
    total: number;
    average_mastery: number;
    need_attention: number;
    quizzes_taken: number;
    students: { name: string; grade: string; mastery: number; status: string }[];
  }>("/api/teacher/students");
}

export async function fetchChildProgress() {
  return api.get<{
    mastery: number;
    subjects: { name: string; mastery: number }[];
    recent_alerts: { type: string; message: string; time: string }[];
  }>("/api/parent/child-progress");
}

export async function fetchBurnoutRisk() {
  return api.get<{ risk_level: string; factors: string[] }>("/api/progress/burnout-risk");
}

export async function sendAudioMessage(audioBlob: Blob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  return api.upload<{ transcript: string; response: string }>("/api/study/voice", formData);
}
