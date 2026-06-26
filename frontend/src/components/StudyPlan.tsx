"use client";

import { useState, useEffect } from "react";
import { fetchStudyPlan } from "@/lib/api";

interface PlanDay {
  day: number;
  title: string;
  focus: string;
  estimated_minutes: number;
  completed: boolean;
}

export function StudyPlan() {
  const [plan, setPlan] = useState<PlanDay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await fetchStudyPlan();
        if (!cancelled) setPlan(data.days || []);
      } catch {
        if (!cancelled) setError("Could not load study plan.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="skeleton h-6 w-40 mb-2" />
            <div className="skeleton h-4 w-52" />
          </div>
          <div className="skeleton h-8 w-16" />
        </div>
        <div className="skeleton h-2 w-full mb-6" />
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="skeleton h-12 w-full mb-2" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-6 text-center">
        <p className="text-2xl mb-2">📚</p>
        <p className="text-surface-400 text-sm">{error}</p>
        <button onClick={() => window.location.reload()} className="btn-secondary text-sm mt-4">
          Retry
        </button>
      </div>
    );
  }

  if (plan.length === 0) {
    return (
      <div className="glass-card p-6 text-center">
        <p className="text-2xl mb-2">📚</p>
        <h3 className="font-semibold mb-1">No Study Plan Yet</h3>
        <p className="text-sm text-surface-400">Start studying and ask for a personalized plan.</p>
      </div>
    );
  }

  const completedCount = plan.filter((d) => d.completed).length;

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Your Study Plan</h3>
          <p className="text-sm text-surface-400">7-Day Adaptive Plan</p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold gradient-text">{completedCount}/{plan.length}</span>
          <p className="text-xs text-surface-500">Days completed</p>
        </div>
      </div>

      <div className="h-2 rounded-full bg-surface-800 mb-6 overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-700"
          style={{ width: `${(completedCount / plan.length) * 100}%` }}
        />
      </div>

      <div className="flex flex-col gap-2">
        {plan.map((day) => (
          <div
            key={day.day}
            className={`flex items-center gap-4 p-3 rounded-xl transition-all ${
              day.completed
                ? "bg-accent-500/5 border border-accent-500/10"
                : "bg-surface-800/20 border border-transparent hover:bg-surface-800/40"
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                day.completed
                  ? "bg-accent-500/20 text-accent-400 scale-105"
                  : "bg-surface-800 text-surface-400"
              }`}
            >
              {day.completed ? "✓" : day.day}
            </div>
            <div className="flex-1">
              <p className={`text-sm font-medium ${day.completed ? "text-surface-400 line-through" : "text-surface-200"}`}>
                {day.title}
              </p>
              <p className="text-xs text-surface-500">{day.focus} · {day.estimated_minutes} min</p>
            </div>
            {day.completed && <span className="text-xs text-accent-400 font-medium">Done</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
