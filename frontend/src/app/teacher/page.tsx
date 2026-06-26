"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Navbar from "@/components/Navbar";
import { fetchStudents, setAuthToken } from "@/lib/api";
import { masteryColor } from "@/lib/utils";
import { getStoredToken, getStoredUser } from "@/lib/auth";

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    excellent: "bg-accent-500/10 text-accent-400 border-accent-500/20",
    "on-track": "bg-primary-500/10 text-primary-300 border-primary-500/20",
    "needs-support": "bg-red-500/10 text-red-400 border-red-500/20",
  };
  const labels: Record<string, string> = { excellent: "Excellent", "on-track": "On Track", "needs-support": "Needs Support" };
  const s = styles[status] || styles["on-track"];
  return <span className={`badge ${s}`}>{labels[status] || status}</span>;
}

export default function TeacherDashboard() {
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
      const d = await fetchStudents();
      setData(d);
    } catch {
      setError("Could not load student data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950">
        <Navbar userName={user?.name} userRole={user?.role} />
        <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
          <div className="skeleton h-8 w-48 mb-2" />
          <div className="skeleton h-4 w-64 mb-8" />
          <div className="grid grid-cols-4 gap-4 mb-8">
            {[1,2,3,4].map(i => <div key={i} className="skeleton h-24 rounded-2xl" />)}
          </div>
          <div className="skeleton h-64 w-full rounded-2xl" />
        </main>
      </div>
    );
  }

  const stats = [
    { value: data ? `${data.total}` : "—", label: "Total Students", icon: "👥", color: "from-primary-500 to-accent-500" },
    { value: data ? `${data.average_mastery}%` : "—", label: "Average Mastery", icon: "📊", color: "from-blue-500 to-cyan-500" },
    { value: data ? `${data.need_attention}` : "—", label: "Need Attention", icon: "⚠️", color: "from-amber-500 to-orange-500" },
    { value: data ? `${data.quizzes_taken}` : "—", label: "Quizzes Taken", icon: "📝", color: "from-purple-500 to-pink-500" },
  ];

  return (
    <div className="min-h-screen bg-surface-950">
      <Navbar userName={user?.name} userRole={user?.role} />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold font-display gradient-text">Teacher Dashboard</h1>
            <p className="text-surface-400 mt-1">Track your students&apos; progress and identify those who need support.</p>
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

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 stagger-children">
          {stats.map((stat) => (
            <div key={stat.label} className="stat-card group">
              <div className="flex items-start justify-between">
                <span className={`stat-value bg-clip-text text-transparent bg-gradient-to-r ${stat.color}`}>{stat.value}</span>
                <span className="text-xl">{stat.icon}</span>
              </div>
              <span className="stat-label">{stat.label}</span>
            </div>
          ))}
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Students Overview</h3>
            {data?.students && data.students.length > 0 && <span className="text-sm text-surface-500">{data.students.length} students</span>}
          </div>

          {data?.students && data.students.length > 0 ? (
            <div className="flex flex-col gap-2">
              {data.students.map((student: any) => (
                <div key={student.name} className="flex items-center justify-between p-3 rounded-xl bg-surface-800/30 hover:bg-surface-800/50 transition-colors group">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-sm font-bold group-hover:scale-105 transition-transform">
                      {student.name.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-surface-200">{student.name}</p>
                      <p className="text-xs text-surface-500">Grade {student.grade}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className={`text-sm font-semibold bg-clip-text text-transparent bg-gradient-to-r ${masteryColor(student.mastery)}`}>
                        {student.mastery}%
                      </p>
                      <p className="text-xs text-surface-500">Mastery</p>
                    </div>
                    <StatusBadge status={student.status} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-10 text-surface-500">
              <p className="text-4xl mb-3">👩‍🏫</p>
              <p className="text-lg mb-2">No student data available yet</p>
              <p className="text-sm">Students will appear here once they start learning with EduMitra.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
