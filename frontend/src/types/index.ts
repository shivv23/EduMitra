export interface StudentProfile {
  id: string;
  role: "student" | "parent" | "teacher" | "admin";
  name?: string;
  email?: string;
  grade?: number;
  preferred_language: string;
  avatar_url?: string;
}

export interface StudyProgress {
  id: string;
  subject: string;
  topic: string;
  mastery_score: number;
  quizzes_taken: number;
  quizzes_passed: number;
  study_plan?: StudyPlanDay[];
}

export interface StudyPlanDay {
  day: number;
  title: string;
  focus: string;
  estimated_minutes: number;
  completed?: boolean;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  type?: "text" | "quiz" | "wellness" | "audio" | "image";
  metadata?: Record<string, unknown>;
}

export interface WellnessCheckIn {
  id: string;
  sentiment_score?: number;
  stress_level?: number;
  crisis_detected: boolean;
  response: string;
  risk_level: "none" | "low" | "medium" | "high";
}

export interface Alert {
  id: string;
  alert_type: "wellness" | "academic" | "burnout_risk";
  severity: "low" | "medium" | "high" | "critical";
  created_at: string;
  resolved_at?: string;
}

export interface Language {
  code: string;
  name: string;
  native: string;
}

export const SUPPORTED_LANGUAGES: Language[] = [
  { code: "en", name: "English", native: "English" },
  { code: "hi", name: "Hindi", native: "हिन्दी" },
  { code: "ta", name: "Tamil", native: "தமிழ்" },
  { code: "te", name: "Telugu", native: "తెలుగు" },
  { code: "bn", name: "Bengali", native: "বাংলা" },
  { code: "mr", name: "Marathi", native: "मराठी" },
  { code: "gu", name: "Gujarati", native: "ગુજરાતી" },
  { code: "kn", name: "Kannada", native: "ಕನ್ನಡ" },
  { code: "ml", name: "Malayalam", native: "മലയാളം" },
  { code: "pa", name: "Punjabi", native: "ਪੰਜਾਬੀ" },
  { code: "ur", name: "Urdu", native: "اردو" },
];
