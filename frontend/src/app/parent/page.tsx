"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Navbar from "@/components/Navbar";
import { fetchChildProgress, setAuthToken } from "@/lib/api";
import { masteryColor } from "@/lib/utils";
import { getStoredToken, getStoredUser } from "@/lib/auth";

export default function ParentDashboard() {
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
      const d = await fetchChildProgress();
      setData(d);
    } catch {
      setError("Could not load child progress data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950">
        <Navbar userName={user?.name} userRole={user?.role} />
        <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
          <div className="skeleton h-8 w-48 mb-2" />
          <div className="skeleton h-4 w-64 mb-8" />
          <div className="grid grid-cols-2 gap-6 mb-8">
            <div className="skeleton h-52 rounded-2xl" />
            <div className="skeleton h-52 rounded-2xl" />
          </div>
          <div className="skeleton h-48 w-full rounded-2xl" />
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
            <h1 className="text-3xl font-bold font-display gradient-text">Parent Dashboard</h1>
            <p className="text-surface-400 mt-1">Stay informed about your child&apos;s learning and well-being.</p>
          </div>
          <button onClick={load} className="btn-icon text-sm flex items-center gap-2" title="Refresh data">
            <svg className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={load} className="px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-xs font-medium transition-colors">Retry</button>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6 mb-8 stagger-children">
          <div className="glass-card p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/5 rounded-full blur-2xl" />
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-accent-500/5 rounded-full blur-2xl" />
            <h3 className="text-lg font-semibold mb-4">Academic Progress</h3>
            <div className="inline-flex items-center justify-center w-28 h-28 rounded-full bg-gradient-to-br from-primary-500/20 to-accent-500/20 border-4 border-primary-500/30 mb-4 animate-pulse-glow">
              <span className="text-3xl font-bold gradient-text">{data ? `${data.mastery}%` : "—"}</span>
            </div>
            <p className="text-sm text-surface-400">
              {data ? "Your child is making progress. Keep encouraging them!" : "Data will appear when your child starts learning."}
            </p>
            {!data && (
              <button onClick={() => router.push("/study")} className="btn-primary text-sm mt-4 glow">
                Encourage Learning
              </button>
            )}
          </div>

          <div className="glass-card p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-accent-500/5 rounded-full blur-2xl" />
            <h3 className="text-lg font-semibold mb-4">Subject Mastery</h3>
            {data?.subjects && data.subjects.length > 0 ? (
              <div className="flex flex-col gap-4">
                {data.subjects.map((s: any) => (
                  <div key={s.name} className="flex items-center gap-3">
                    <span className="w-20 text-xs text-surface-400">{s.name}</span>
                    <div className="flex-1 h-3 rounded-full bg-surface-800 overflow-hidden">
                      <div className={`h-full rounded-full bg-gradient-to-r ${masteryColor(s.mastery)} transition-all duration-700`} style={{ width: `${s.mastery}%` }} />
                    </div>
                    <span className="text-xs font-medium text-surface-300 w-8 text-right">{s.mastery}%</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-[180px] text-surface-500">
                <p className="text-3xl mb-2">📚</p>
                <p className="text-sm">No subjects tracked yet.</p>
              </div>
            )}
          </div>
        </div>

        <div className="glass-card p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>🔔</span> Recent Alerts
          </h3>
          {data?.recent_alerts && data.recent_alerts.length > 0 ? (
            <div className="flex flex-col gap-2">
              {data.recent_alerts.map((alert: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-surface-800/30 hover:bg-surface-800/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <span className={`w-2 h-2 rounded-full ${alert.type === "wellness" ? "bg-purple-400 animate-pulse" : "bg-primary-400"}`} />
                    <p className="text-sm text-surface-200">{alert.message}</p>
                  </div>
                  <span className="text-xs text-surface-500">{alert.time}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-surface-500">
              <p className="text-4xl mb-3">✅</p>
              <p className="text-lg mb-1">No alerts</p>
              <p className="text-sm">Everything looks good. Alerts about your child&apos;s progress will appear here.</p>
            </div>
          )}
        </div>

        <div className="glass-card p-6 bg-gradient-to-br from-accent-500/5 to-emerald-500/5 hover:from-accent-500/10 hover:to-emerald-500/10 transition-all duration-300">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <span className="text-xl">💡</span> Tips for Parents
          </h3>
          <ul className="text-sm text-surface-400 space-y-2">
            <li className="flex items-start gap-2"><span className="text-accent-400 mt-0.5">•</span> Encourage regular short breaks during study sessions</li>
            <li className="flex items-start gap-2"><span className="text-accent-400 mt-0.5">•</span> Celebrate small wins to build confidence</li>
            <li className="flex items-start gap-2"><span className="text-accent-400 mt-0.5">•</span> Ask open-ended questions about what they learned</li>
            <li className="flex items-start gap-2"><span className="text-accent-400 mt-0.5">•</span> Ensure a quiet, distraction-free study space</li>
            <li className="flex items-start gap-2"><span className="text-accent-400 mt-0.5">•</span> Monitor screen time and encourage physical activity</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
