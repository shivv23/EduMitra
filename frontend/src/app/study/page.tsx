"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import { ChatInterface } from "@/components/ChatInterface";
import { FileUpload } from "@/components/FileUpload";
import { VoiceRecorder } from "@/components/VoiceRecorder";
import { QuizCard } from "@/components/QuizCard";
import { SUPPORTED_LANGUAGES } from "@/types";
import { setAuthToken } from "@/lib/api";
import { getStoredToken, getStoredUser } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://edumitra-ai.onrender.com";

export default function StudyPage() {
  const router = useRouter();
  const [showUpload, setShowUpload] = useState(false);
  const [showQuiz, setShowQuiz] = useState(false);
  const [language, setLanguage] = useState("hi");
  const [activeTab, setActiveTab] = useState("chat");
  const [voiceText, setVoiceText] = useState("");
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState<{ name: string; role: string } | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    const user = getStoredUser();
    if (!token || !user) { router.push("/login"); return; }
    setAuthToken(token);
    setUser({ name: user.name, role: user.role });
    setReady(true);
  }, [router]);

  useEffect(() => {
    const keepWarm = setInterval(() => {
      fetch(`${API_BASE}/health`).catch(() => {});
    }, 600000);
    return () => clearInterval(keepWarm);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("upload") === "true") setShowUpload(true);
  }, []);

  const handleChatUploadClick = useCallback(() => {
    document.getElementById("study-file-input")?.click();
  }, []);

  if (!ready) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <div className="w-6 h-6 rounded-full border-2 border-primary-500/30 border-t-primary-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-950 flex flex-col">
      <Navbar userName={user?.name} userRole={user?.role} />

      <main className="flex-1 flex flex-col max-w-5xl mx-auto w-full px-4 sm:px-6 py-6 animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold font-display gradient-text">Study Room</h1>
            <p className="text-surface-400 text-sm mt-0.5">Ask anything — your AI tutor understands text, images, and voice.</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 bg-surface-800/50 rounded-lg p-1">
              <button
                type="button"
                onClick={() => setActiveTab("chat")}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                  activeTab === "chat" ? "bg-primary-500/20 text-primary-300 shadow-sm" : "text-surface-400 hover:text-surface-200"
                }`}
              >
                💬 Chat
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("voice")}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                  activeTab === "voice" ? "bg-primary-500/20 text-primary-300 shadow-sm" : "text-surface-400 hover:text-surface-200"
                }`}
              >
                🎤 Voice
              </button>
              <button
                type="button"
                onClick={() => setShowQuiz(!showQuiz)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                  showQuiz ? "bg-primary-500/20 text-primary-300 shadow-sm" : "text-surface-400 hover:text-surface-200"
                }`}
              >
                📝 Quiz
              </button>
            </div>
            <span className="badge-primary">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-400 animate-pulse" />
              Tutor Active
            </span>
          </div>
        </div>

        {activeTab === "voice" && ready && (
          <div className="mb-6 animate-slide-up">
            <div className="flex items-center gap-2 mb-3">
              <label className="text-sm text-surface-400">Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="input-premium w-auto py-1.5 text-sm"
              >
                {SUPPORTED_LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>{l.native} ({l.name})</option>
                ))}
              </select>
            </div>
            <VoiceRecorder language={language} onResult={(text) => {
              setVoiceText(text);
              setActiveTab("chat");
            }} />
          </div>
        )}

        {showQuiz && ready && (
          <div className="mb-6 animate-slide-up">
            <QuizCard />
          </div>
        )}

        <input
          id="study-file-input"
          type="file"
          accept="image/jpeg,image/png,image/webp,application/pdf"
          className="hidden"
          onChange={(e) => {
            if (e.target.files?.[0]) setShowUpload(true);
          }}
        />

        {showUpload && (
          <div className="mb-6 animate-slide-up">
            <FileUpload />
            <div className="flex justify-end mt-2">
              <button
                type="button"
                onClick={() => setShowUpload(false)}
                className="text-xs text-surface-500 hover:text-surface-300 transition-colors px-2 py-1 rounded hover:bg-surface-800/30"
              >
                ✕ Close upload panel
              </button>
            </div>
          </div>
        )}

        <div className="flex-1 flex flex-col glass-strong rounded-2xl overflow-hidden min-h-[400px]">
          <ChatInterface onUploadClick={handleChatUploadClick} externalText={voiceText} />
        </div>

        <div className="flex items-center justify-between mt-3 text-xs text-surface-500">
          <div className="flex items-center gap-4">
            <span>EduMitra uses RAG-grounded AI. Responses are age-appropriate.</span>
            <kbd className="hidden sm:inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-surface-800/50 text-surface-500 text-[10px] border border-surface-700/50">
              Ctrl+Enter
            </kbd>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowUpload(!showUpload)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-surface-800/40 text-surface-500 hover:text-surface-300 transition-all active:scale-95"
            >
              <span>📸</span> {showUpload ? "Hide Upload" : "Upload Notes"}
            </button>
            <button
              type="button"
              onClick={() => { setActiveTab("voice"); }}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-surface-800/40 text-surface-500 hover:text-surface-300 transition-all active:scale-95"
            >
              <span>🎤</span> Voice
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
