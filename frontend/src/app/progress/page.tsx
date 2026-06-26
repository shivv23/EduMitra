"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Navbar from "@/components/Navbar";
import { fetchProgress, setAuthToken } from "@/lib/api";
import { masteryColor, masteryLabel } from "@/lib/utils";
import { getStoredToken, getStoredUser } from "@/lib/auth";

export default function ProgressPage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<{ name: string; role: string } | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    const user = getStoredUser();
    if (!token || !user) { router.push("/login"); return; }
    setAuthToken(token);
    setUser({ name: user.name, role: user.role });
  }, [router]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const d = await fetchProgress();
      setData(d);
    } catch {
      setError("Could not load progress data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);
  const subjects = data?.subjects || [];
  const activities = data?.recent_activity || [];

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950">
        <Navbar userName={user?.name} userRole={user?.role} />
        <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
          <div className="skeleton h-8 w-48 mb-2" />
          <div className="skeleton h-4 w-64 mb-8" />
          <div className="skeleton h-48 w-full mb-6 rounded-2xl" />
          <div className="skeleton h-64 w-full rounded-2xl" />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-950">
      <Navbar userName={user?.name} userRole={user?.role} />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold font-display gradient-text">Learning Progress</h1>
            <p className="text-surface-400 mt-1">Track your mastery across subjects.</p>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="badge-accent">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-400" />
              {data ? "Updated today" : "Sign in to track"}
            </span>
            <button onClick={load} className="btn-icon text-xs" title="Refresh">
              <svg className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={load} className="px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-xs font-medium transition-colors">Retry</button>
          </div>
        )}

        <div className="glass-card p-8 mb-8 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-40 h-40 bg-primary-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-accent-500/5 rounded-full blur-3xl" />
          <div className="inline-flex items-center justify-center w-36 h-36 rounded-full bg-gradient-to-br from-primary-500/20 to-accent-500/20 border-4 border-primary-500/30 mb-4 animate-pulse-glow relative">
            <span className="text-4xl font-bold gradient-text">{data ? `${data.overall_mastery}%` : "—"}</span>
          </div>
          <h2 className="text-xl font-semibold">Overall Mastery Score</h2>
          <p className="text-surface-400 mt-1">
            {data ? `You're on a ${masteryLabel(data.overall_mastery).toLowerCase()} streak. Keep it up!` : "Start studying to track your progress."}
          </p>
          {!data && (
            <button onClick={() => router.push("/study")} className="btn-primary text-sm mt-6 glow">
              Start Studying
            </button>
          )}
        </div>

        <div className="glass-card p-6 mb-6">
          <h3 className="text-lg font-semibold mb-6">Subject Breakdown</h3>
          {subjects.length > 0 ? (
            <div className="flex flex-col gap-5">
              {subjects.map((subject: any) => (
                <div key={subject.name} className="flex items-center gap-4 group">
                  <div className="w-24 text-sm font-medium text-surface-300">{subject.name}</div>
                  <div className="flex-1 h-3 rounded-full bg-surface-800 overflow-hidden relative">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${masteryColor(subject.mastery)} transition-all duration-1000 group-hover:opacity-80`}
                      style={{ width: `${subject.mastery}%` }}
                    />
                  </div>
                  <div className="w-12 text-right text-sm font-semibold text-surface-200">{subject.mastery}%</div>
                  <div className="w-10 text-right text-xs text-accent-400">{subject.trend}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-10 text-surface-500">
              <p className="text-4xl mb-3">📊</p>
              <p className="text-lg mb-2">No subjects tracked yet</p>
              <p className="text-sm mb-6">Start studying to see your progress breakdown.</p>
              <button onClick={() => router.push("/study")} className="btn-primary text-sm glow">Start Studying</button>
            </div>
          )}
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          {activities.length > 0 ? (
            <div className="flex flex-col gap-3">
              {activities.map((item: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-surface-800/30 hover:bg-surface-800/50 transition-colors">
                  <div>
                    <p className="text-sm font-medium text-surface-200">{item.action}</p>
                    <p className="text-xs text-surface-500">{item.detail}</p>
                  </div>
                  <span className="text-xs text-surface-500">{item.time}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-10 text-surface-500">
              <p className="text-4xl mb-3">📋</p>
              <p className="text-lg mb-2">No activity yet</p>
              <p className="text-sm">Your recent actions will appear here once you start learning.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
