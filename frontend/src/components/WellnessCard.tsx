"use client";

import { useState } from "react";
import { wellnessCheckIn } from "@/lib/api";

export function WellnessCard() {
  const [sentiment, setSentiment] = useState<number | null>(null);
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleMood(value: number) {
    setSentiment(value);
    setSending(true);
    try {
      const result = await wellnessCheckIn(value);
      setMessage(result.response);
    } catch {
      setMessage("Thanks for checking in. Take care of yourself! ❤️");
    } finally {
      setSending(false);
    }
  }

  const moods = [
    { value: 1, emoji: "😢", label: "Tough" },
    { value: 2, emoji: "😕", label: "Down" },
    { value: 3, emoji: "😐", label: "Okay" },
    { value: 4, emoji: "🙂", label: "Good" },
    { value: 5, emoji: "😊", label: "Great" },
  ];

  return (
    <div className="glass-card p-6 bg-gradient-to-br from-purple-500/5 to-pink-500/5 border-purple-500/10">
      <div className="flex items-center gap-3 mb-3">
        <span className="text-2xl animate-float">🧠</span>
        <div>
          <h3 className="font-semibold">Wellness Check</h3>
          <p className="text-xs text-surface-400">How are you feeling?</p>
        </div>
      </div>

      {sending ? (
        <div className="flex justify-center py-4">
          <svg className="w-6 h-6 animate-spin text-primary-400" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        </div>
      ) : message ? (
        <div className="p-3 rounded-xl bg-surface-800/30 text-sm text-surface-300 animate-fade-in">
          {message}
        </div>
      ) : sentiment === null ? (
        <div className="flex gap-2 my-3">
          {moods.map((m) => (
            <button
              key={m.value}
              onClick={() => handleMood(m.value)}
              className="flex-1 p-2 rounded-lg bg-surface-800/30 hover:bg-surface-800/60 text-xl transition-all hover:scale-110 active:scale-95"
              title={m.label}
            >
              {m.emoji}
            </button>
          ))}
        </div>
      ) : null}

      <p className="text-xs text-surface-500 text-center mt-2">
        Quick check-in takes 10 seconds. Your data is encrypted and private.
      </p>
    </div>
  );
}

export function WellnessCheckInCard() {
  const [sentiment, setSentiment] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState<{ response: string; risk_level: string } | null>(null);

  async function handleCheckIn() {
    if (sentiment === null) return;
    setSending(true);
    try {
      const data = await wellnessCheckIn(sentiment, note || undefined);
      setResult(data);
    } catch {
      setResult({ response: "Thanks for sharing. Remember, you're not alone — reach out if you need help.", risk_level: "none" });
    } finally {
      setSending(false);
    }
  }

  const moods = [
    { value: 1, emoji: "😢", label: "Struggling", color: "from-red-500/20 to-red-500/5" },
    { value: 2, emoji: "😕", label: "Down", color: "from-orange-500/20 to-orange-500/5" },
    { value: 3, emoji: "😐", label: "Okay", color: "from-yellow-500/20 to-yellow-500/5" },
    { value: 4, emoji: "🙂", label: "Good", color: "from-primary-500/20 to-primary-500/5" },
    { value: 5, emoji: "😊", label: "Great", color: "from-accent-500/20 to-accent-500/5" },
  ];

  if (result) {
    return (
      <div className="glass-card p-8 text-center animate-slide-up">
        <span className="text-5xl mb-4 block">
          {result.risk_level === "high" ? "💙" : result.risk_level === "medium" ? "💛" : "💚"}
        </span>
        <h2 className="text-2xl font-bold font-display mb-2">Thank You</h2>
        <p className="text-surface-300 mb-4">{result.response}</p>
        {result.risk_level === "high" && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-300 mb-4">
            Please reach out to a trusted adult or call a helpline. You matter. ❤️
          </div>
        )}
        <button onClick={() => { setResult(null); setSentiment(null); setNote(""); }} className="btn-secondary text-sm">
          Check In Again
        </button>
      </div>
    );
  }

  return (
    <div className="glass-card p-8 text-center">
      <span className="text-5xl mb-4 block animate-float">🧠</span>
      <h2 className="text-2xl font-bold font-display mb-2">How are you feeling today?</h2>
      <p className="text-surface-400 mb-6">Be honest — this helps me support you better. Everything is confidential.</p>

      <div className="flex justify-center gap-3 mb-8">
        {moods.map((m) => (
          <button
            key={m.value}
            onClick={() => setSentiment(m.value)}
            className={`flex flex-col items-center gap-1.5 p-4 rounded-xl bg-gradient-to-b ${m.color} border transition-all ${
              sentiment === m.value
                ? "border-primary-500/50 scale-110 shadow-lg shadow-primary-500/20"
                : "border-surface-700/30 hover:border-surface-600/50 hover:scale-105"
            } active:scale-95`}
          >
            <span className="text-3xl">{m.emoji}</span>
            <span className="text-xs text-surface-400">{m.label}</span>
          </button>
        ))}
      </div>

      <div className="max-w-md mx-auto">
        <textarea
          placeholder="Want to share more? (optional)"
          rows={3}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          className="input-premium mb-4"
        />
        <button
          onClick={handleCheckIn}
          disabled={sentiment === null || sending}
          className="btn-primary w-full glow"
        >
          {sending ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Sending...
            </span>
          ) : "Send Check-In"}
        </button>
      </div>

      <p className="text-xs text-surface-500 mt-4">
        I&apos;m a wellness companion, not a therapist. If you&apos;re in crisis, please call a helpline.
      </p>
    </div>
  );
}
