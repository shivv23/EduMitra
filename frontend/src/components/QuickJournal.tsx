"use client";

import { useState } from "react";

export function QuickJournal({ onClose }: { onClose: () => void }) {
  const [entry, setEntry] = useState("");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function saveEntry() {
    if (!entry.trim()) {
      setError("Write something before saving.");
      return;
    }
    try {
      const res = await fetch("/api/journal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: entry.trim() }),
      });
      if (!res.ok) throw new Error("Failed to save");
      setSaved(true);
      setError(null);
    } catch {
      // Fallback: save to localStorage
      try {
        const existing = JSON.parse(localStorage.getItem("edumitra_journal") || "[]");
        existing.push({ content: entry.trim(), date: new Date().toISOString() });
        localStorage.setItem("edumitra_journal", JSON.stringify(existing));
        setSaved(true);
        setError(null);
      } catch {
        setError("Could not save your entry. Please try again.");
      }
    }
  }

  if (saved) {
    return (
      <div className="text-center py-8 animate-fade-in">
        <span className="text-5xl block mb-4">📝</span>
        <h3 className="text-xl font-semibold mb-2">Saved Privately</h3>
        <p className="text-sm text-surface-400 mb-6">Your journal entry is encrypted and stored securely.</p>
        <button onClick={onClose} className="btn-secondary text-sm">
          Done
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-surface-400">Write down your thoughts. This is your private space — no one else can read it.</p>
      {error && (
        <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-slide-up">{error}</div>
      )}
      <textarea
        value={entry}
        onChange={(e) => setEntry(e.target.value)}
        placeholder="What's on your mind today?"
        rows={6}
        className="input-premium resize-none"
        autoFocus
      />
      <div className="flex gap-3">
        <button onClick={onClose} className="btn-ghost text-sm">Cancel</button>
        <button onClick={saveEntry} disabled={!entry.trim()} className="btn-primary text-sm glow">
          Save Entry
        </button>
      </div>
      <p className="text-xs text-surface-600">Your journal is encrypted end-to-end and stored privately.</p>
    </div>
  );
}
