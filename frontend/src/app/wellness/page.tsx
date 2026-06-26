"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import { WellnessCheckInCard } from "@/components/WellnessCard";
import { Modal } from "@/components/Modal";
import { BreathingExercise } from "@/components/BreathingExercise";
import { QuickJournal } from "@/components/QuickJournal";
import { fetchWellnessHistory, setAuthToken } from "@/lib/api";
import { getStoredToken, getStoredUser } from "@/lib/auth";

const HELPLINES = [
  { name: "iCall Helpline", phone: "9152987821", desc: "Mental health support" },
  { name: "Vandrevala Foundation", phone: "9999666555", desc: "24x7 crisis support" },
  { name: "KIRAN Helpline", phone: "18005990019", desc: "Mental Health Rehabilitation" },
  { name: "AASRA", phone: "9820466726", desc: "Suicide prevention" },
  { name: "Childline India", phone: "1098", desc: "Children in distress" },
];

export default function WellnessPage() {
  const router = useRouter();
  const [breathingOpen, setBreathingOpen] = useState(false);
  const [journalOpen, setJournalOpen] = useState(false);
  const [trendData, setTrendData] = useState<number[] | null>(null);
  const [checkins, setCheckins] = useState<{ sentiment_score: number; created_at: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<{ name: string; role: string } | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    const user = getStoredUser();
    if (!token || !user) { router.push("/login"); return; }
    setAuthToken(token);
    setUser({ name: user.name, role: user.role });
  }, [router]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchWellnessHistory();
        if (data?.checkins) {
          setCheckins(data.checkins);
          setTrendData(data.checkins.map((c: any) => c.sentiment_score * 20));
        }
      } catch {
        setTrendData([30, 45, 25, 60, 40, 55, 35]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-surface-950">
      <Navbar userName={user?.name} userRole={user?.role} />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 mb-4 shadow-lg shadow-purple-500/20 animate-float glow-purple">
            <span className="text-2xl">🧠</span>
          </div>
          <h1 className="text-3xl font-bold font-display">Wellness Corner</h1>
          <p className="text-surface-400 mt-2 max-w-lg mx-auto">
            Your well-being matters as much as your studies. Check in, breathe, and take care of yourself. Everything you share is private and encrypted.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="md:col-span-2">
            <WellnessCheckInCard />
          </div>

          <div className="glass-card p-6 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 group cursor-pointer hover:scale-[1.02] transition-all duration-300" onClick={() => setBreathingOpen(true)}>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <span className="text-2xl group-hover:animate-pulse">🌬️</span> Breathing Exercise
            </h3>
            <p className="text-sm text-surface-400 mb-4">
              Take a 60-second calming break. Breathe in for 4 seconds, hold for 4, breathe out for 4.
            </p>
            <button className="btn-primary w-full text-sm glow" onClick={(e) => { e.stopPropagation(); setBreathingOpen(true); }}>
              Start 60s Session
            </button>
          </div>

          <div className="glass-card p-6 bg-gradient-to-br from-amber-500/5 to-orange-500/5 group cursor-pointer hover:scale-[1.02] transition-all duration-300" onClick={() => setJournalOpen(true)}>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <span className="text-2xl group-hover:animate-pulse">📝</span> Quick Journal
            </h3>
            <p className="text-sm text-surface-400 mb-4">
              Writing down how you feel can help reduce stress. Your journal is private and encrypted.
            </p>
            <button className="btn-secondary w-full text-sm" onClick={(e) => { e.stopPropagation(); setJournalOpen(true); }}>Write Now</button>
          </div>

          <div className="glass-card p-6 md:col-span-2 bg-gradient-to-br from-purple-500/5 to-pink-500/5">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <span>📞</span> Helplines — 24x7 Support
            </h3>
            <div className="grid sm:grid-cols-2 gap-3">
              {HELPLINES.map((h) => (
                <div key={h.name} className="flex items-center justify-between p-3 rounded-xl bg-surface-800/30 hover:bg-surface-800/60 transition-colors group">
                  <div>
                    <p className="text-sm font-medium text-surface-200">{h.name}</p>
                    <p className="text-xs text-surface-500">{h.desc}</p>
                  </div>
                  <a href={`tel:${h.phone}`} className="px-3 py-1.5 rounded-lg bg-primary-500/10 hover:bg-primary-500/20 text-primary-300 text-sm font-medium transition-all hover:scale-105 active:scale-95">
                    {h.phone}
                  </a>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-6 bg-gradient-to-br from-purple-500/5 to-pink-500/5">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <span>📈</span> Your Wellness Trend
            </h3>
            {loading ? (
              <div className="space-y-3">
                <div className="skeleton h-24 w-full" />
              </div>
            ) : checkins.length > 0 ? (
              <div>
                <p className="text-xs text-surface-500 mb-3">Your check-ins over time</p>
                <div className="h-24 flex items-end gap-2">
                  {checkins.slice(-7).map((c, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1 group/chart">
                      <div
                        className="w-full bg-gradient-to-t from-purple-500/40 to-pink-500/20 rounded-t-lg transition-all duration-500 hover:from-purple-500/70 min-h-[4px]"
                        style={{ height: `${c.sentiment_score * 20}%` }}
                      />
                      <span className="text-[10px] text-surface-600 opacity-0 group-hover/chart:opacity-100 transition-opacity">
                        {["😢","😕","😐","🙂","😊"][c.sentiment_score - 1] || "😐"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div>
                <p className="text-sm text-surface-400 mb-4">
                  Your sentiment trends will appear here after your first check-in.
                </p>
                <div className="h-24 flex items-end gap-2">
                  {[30, 45, 25, 60, 40, 55, 35].map((h, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1">
                      <div
                        className="w-full bg-gradient-to-t from-purple-500/30 to-pink-500/10 rounded-t-lg transition-all duration-500 hover:from-purple-500/50"
                        style={{ height: `${h}%` }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 p-4 rounded-xl bg-amber-500/5 border border-amber-500/10 text-sm text-surface-400">
          <p className="font-medium text-amber-300 mb-1">Important</p>
          <p>
            EduMitra AI is a wellness companion, not a substitute for professional medical advice, diagnosis, or treatment.
            If you&apos;re in crisis, please call a helpline or reach out to a trusted adult. Your safety is our top priority.
          </p>
        </div>
      </main>

      <Modal open={breathingOpen} onClose={() => setBreathingOpen(false)} title="Breathing Exercise" maxWidth="max-w-md">
        <BreathingExercise onClose={() => setBreathingOpen(false)} />
      </Modal>

      <Modal open={journalOpen} onClose={() => setJournalOpen(false)} title="Quick Journal" maxWidth="max-w-md">
        <QuickJournal onClose={() => setJournalOpen(false)} />
      </Modal>
    </div>
  );
}
