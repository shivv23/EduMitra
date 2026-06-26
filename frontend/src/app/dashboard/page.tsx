"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Link from "next/link";
import { StudyPlan } from "@/components/StudyPlan";
import { WellnessCard } from "@/components/WellnessCard";
import { fetchDashboard, setAuthToken } from "@/lib/api";
import { getStoredToken, getStoredUser } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<{
    overall_mastery: number;
    topics_covered: number;
    quizzes_taken: number;
    streak: number;
    wellness_status: string;
    last_checkin?: string;
  } | null>(null);
  const [user, setUser] = useState<{ name: string; role: string } | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    const user = getStoredUser();
    if (!token || !user) {
      router.push("/login");
      return;
    }
    setAuthToken(token);
    setUser({ name: user.name, role: user.role });
  }, [router]);

  useEffect(() => {
    if (user) fetchDashboard().then(setData).catch(() => {});
  }, [user]);

  const stats = [
    { value: data ? `${data.overall_mastery}%` : "—", label: "Overall Mastery", trend: data ? "Updated today" : "Sign in to see", color: "from-primary-500 to-accent-500" },
    { value: data ? `${data.topics_covered}` : "—", label: "Topics Covered", trend: data ? "Keep learning!" : "", color: "from-blue-500 to-cyan-500" },
    { value: data ? `${data.quizzes_taken}` : "—", label: "Quizzes Taken", trend: data ? "Practice makes perfect" : "", color: "from-purple-500 to-pink-500" },
    { value: data ? `${data.streak}` : "—", label: "Day Streak", trend: data ? "🔥 Keep going!" : "", color: "from-accent-500 to-emerald-500" },
  ];

  return (
    <div className="min-h-screen bg-surface-950">
      <Navbar userName={user?.name} userRole={user?.role} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold font-display">
              Welcome back, <span className="gradient-text">{user?.name?.split(" ")[0]}</span>
            </h1>
            <p className="text-surface-400 mt-1">Here&apos;s your learning overview for today.</p>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/study" className="btn-primary glow">
              <span className="flex items-center gap-2">📝 Start Studying</span>
            </Link>
            <Link href="/wellness" className="btn-secondary">
              <span className="flex items-center gap-2">🧠 Check In</span>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat) => (
            <div key={stat.label} className="stat-card group">
              <div className="flex items-start justify-between">
                <span className={`stat-value bg-clip-text text-transparent bg-gradient-to-r ${stat.color}`}>
                  {stat.value}
                </span>
                <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${stat.color} opacity-60 group-hover:opacity-100 transition-opacity`} />
              </div>
              <span className="stat-label">{stat.label}</span>
              {stat.trend && <span className="text-xs text-surface-500">{stat.trend}</span>}
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <StudyPlan />
          </div>

          <div className="flex flex-col gap-6">
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="flex flex-col gap-2">
                <Link href="/study" className="flex items-center gap-3 p-3 rounded-xl bg-surface-800/50 hover:bg-surface-800 transition-colors group">
                  <span className="text-xl">📝</span>
                  <div>
                    <p className="text-sm font-medium text-surface-200 group-hover:text-primary-300 transition-colors">Ask a Question</p>
                    <p className="text-xs text-surface-500">Get instant explanations</p>
                  </div>
                </Link>
                <Link href="/study?upload=true" className="flex items-center gap-3 p-3 rounded-xl bg-surface-800/50 hover:bg-surface-800 transition-colors group">
                  <span className="text-xl">📸</span>
                  <div>
                    <p className="text-sm font-medium text-surface-200 group-hover:text-primary-300 transition-colors">Upload Notes</p>
                    <p className="text-xs text-surface-500">Analyze handwritten notes</p>
                  </div>
                </Link>
                <Link href="/wellness" className="flex items-center gap-3 p-3 rounded-xl bg-surface-800/50 hover:bg-surface-800 transition-colors group">
                  <span className="text-xl">🧠</span>
                  <div>
                    <p className="text-sm font-medium text-surface-200 group-hover:text-primary-300 transition-colors">Wellness Check</p>
                    <p className="text-xs text-surface-500">How are you feeling?</p>
                  </div>
                </Link>
                <Link href="/progress" className="flex items-center gap-3 p-3 rounded-xl bg-surface-800/50 hover:bg-surface-800 transition-colors group">
                  <span className="text-xl">📊</span>
                  <div>
                    <p className="text-sm font-medium text-surface-200 group-hover:text-primary-300 transition-colors">View Progress</p>
                    <p className="text-xs text-surface-500">Track your mastery</p>
                  </div>
                </Link>
              </div>
            </div>

            <WellnessCard />
          </div>
        </div>
      </main>
    </div>
  );
}
