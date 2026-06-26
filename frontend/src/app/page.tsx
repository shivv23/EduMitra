import Link from "next/link";

const FEATURES = [
  { icon: "📚", title: "Personalized Learning", desc: "AI creates adaptive study plans from your syllabus and performance, tailored just for you.", href: "/study", color: "from-primary-500/20 to-accent-500/5" },
  { icon: "🧠", title: "Mental Wellness", desc: "Proactive stress detection with supportive coaching and verified crisis helplines.", href: "/wellness", color: "from-purple-500/20 to-pink-500/5" },
  { icon: "🗣️", title: "15+ Indian Languages", desc: "Voice-first learning in Hindi, Tamil, Bengali, Marathi, and more.", href: "/study", color: "from-blue-500/20 to-cyan-500/5" },
  { icon: "👁️", title: "Multimodal AI", desc: "Upload handwritten notes, diagrams, or photos — AI understands them instantly.", href: "/study", color: "from-amber-500/20 to-orange-500/5" },
  { icon: "📊", title: "Smart Progress", desc: "Mastery scores, burnout prediction, and real-time parent/teacher alerts.", href: "/progress", color: "from-emerald-500/20 to-accent-500/5" },
  { icon: "💬", title: "WhatsApp Ready", desc: "Learn anytime via WhatsApp — no app download needed.", href: "/study", color: "from-accent-500/20 to-emerald-500/5" },
];

const STATS = [
  { value: "260M+", label: "Students Reached", color: "from-primary-400 to-accent-400" },
  { value: "15+", label: "Indian Languages", color: "from-blue-400 to-cyan-400" },
  { value: "6", label: "AI Agents", color: "from-accent-400 to-emerald-400" },
];

export default async function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="fixed inset-0 bg-gradient-to-br from-surface-950 via-surface-900 to-surface-950" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(236,122,18,0.08),transparent_50%)]" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(26,165,62,0.06),transparent_50%)]" />
      <div className="fixed top-20 left-1/4 w-[600px] h-[600px] bg-primary-500/5 rounded-full blur-3xl animate-float" />
      <div className="fixed bottom-20 right-1/4 w-[500px] h-[500px] bg-accent-500/5 rounded-full blur-3xl animate-float" style={{ animationDelay: "3s" }} />
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-500/3 rounded-full blur-3xl animate-pulse-soft" />

      <nav className="relative z-50 border-b border-surface-800/50 bg-surface-950/80 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="flex items-center gap-3">
            <svg viewBox="0 0 32 32" fill="none" className="w-10 h-10">
              <path d="M16 4C9.373 4 4 9.373 4 16s5.373 12 12 12 12-5.373 12-12S22.627 4 16 4z" fill="currentColor" opacity="0.2" className="text-primary-500" />
              <path d="M16 8c-4.418 0-8 3.582-8 8s3.582 8 8 8 8-3.582 8-8-3.582-8-8-8z" fill="currentColor" opacity="0.4" className="text-primary-400" />
              <path d="M16 12c-2.209 0-4 1.791-4 4s1.791 4 4 4 4-1.791 4-4-1.791-4-4-4z" fill="currentColor" opacity="0.6" className="text-accent-400" />
              <circle cx="16" cy="16" r="2" fill="currentColor" className="text-white" />
              <path d="M16 2v4M16 26v4M6 6l3 3M23 23l3 3M4 16h4M24 16h4M6 26l3-3M23 9l3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" className="text-primary-500" />
            </svg>
            <span className="text-xl font-bold font-display">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-300 via-primary-400 to-accent-400">EduMitra</span>
            </span>
          </span>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="btn-primary text-sm glow">Dashboard</Link>
            <Link href="/login" className="btn-ghost text-sm">Sign In</Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-32">
        <div className="flex flex-col items-center text-center gap-8 max-w-4xl mx-auto animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-300 text-sm font-medium shimmer">
            <span className="w-2 h-2 rounded-full bg-primary-400 animate-pulse" />
            Multi-Agent GenAI Platform
          </div>

          <h1 className="text-5xl md:text-7xl font-bold font-display leading-tight">
            Learn Better,
            <br />
            <span className="gradient-text shimmer-text">Stress Less</span>
          </h1>

          <p className="text-xl text-surface-400 max-w-2xl leading-relaxed">
            Your 24x7 personal AI tutor + wellness companion. Get personalized study plans,
            illustrated explanations, and mental health support — all in your mother tongue.
          </p>

          <div className="flex items-center gap-4 flex-wrap justify-center">
            <Link href="/dashboard" className="btn-primary text-lg px-8 py-4 glow">
              <span className="flex items-center gap-2">Go to Dashboard <span>→</span></span>
            </Link>
            <a href="#features" className="btn-secondary text-lg px-8 py-4">
              Explore Features
            </a>
          </div>

          <div className="grid grid-cols-3 gap-8 mt-16 w-full max-w-2xl">
            {STATS.map((stat) => (
              <div key={stat.label} className="text-center group">
                <div className={`text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r ${stat.color} transition-all duration-500 group-hover:scale-110`}>
                  {stat.value}
                </div>
                <div className="text-sm text-surface-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div id="features" className="grid md:grid-cols-3 gap-6 mt-32 max-w-5xl mx-auto stagger-children">
          {FEATURES.map((feature, i) => (
            <Link
              key={feature.title}
              href={feature.href}
              className={`glass-card-hover p-6 flex flex-col gap-3 group bg-gradient-to-br ${feature.color} cursor-pointer`}
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <span className="text-3xl transition-transform duration-300 group-hover:scale-110 group-hover:animate-pulse">{feature.icon}</span>
              <h3 className="text-lg font-semibold text-surface-100 group-hover:text-primary-300 transition-colors">
                {feature.title}
              </h3>
              <p className="text-sm text-surface-400 leading-relaxed">{feature.desc}</p>
              <div className="mt-auto flex items-center gap-1 text-xs font-medium text-primary-400 group-hover:text-primary-300 transition-all group-hover:gap-2">
                <span>Learn more</span>
                <span className="transition-transform duration-300 group-hover:translate-x-1">→</span>
              </div>
            </Link>
          ))}
        </div>

        <div className="mt-32 max-w-4xl mx-auto text-center glass-card-hover p-12 rounded-3xl bg-gradient-to-br from-primary-500/5 to-accent-500/5 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-accent-500/10 rounded-full blur-3xl" />
          <span className="text-5xl block mb-6 relative">🚀</span>
          <h2 className="text-3xl md:text-4xl font-bold font-display mb-4 relative">Ready to Transform Your Learning?</h2>
          <p className="text-surface-400 text-lg mb-8 max-w-xl mx-auto relative">
            Join millions of Indian students learning smarter, not harder — with AI that speaks your language.
          </p>
          <Link href="/dashboard" className="btn-primary text-lg px-8 py-4 glow relative">Go to Dashboard</Link>
        </div>
      </main>

      <footer className="relative z-10 border-t border-surface-800/50 py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-surface-500">
          <div className="flex items-center gap-2">
            <svg viewBox="0 0 32 32" fill="none" className="w-6 h-6">
              <path d="M16 4C9.373 4 4 9.373 4 16s5.373 12 12 12 12-5.373 12-12S22.627 4 16 4z" fill="currentColor" opacity="0.2" className="text-primary-500" />
              <circle cx="16" cy="16" r="2" fill="currentColor" className="text-primary-400" />
            </svg>
            <span>EduMitra AI</span>
          </div>
          <p>For India&apos;s students — learn better, stress less, in your own language.</p>
          <p>Team CodyRhodes</p>
        </div>
      </footer>
    </div>
  );
}
