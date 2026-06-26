"use client";

import { useState, Suspense } from "react";
import { useRouter } from "next/navigation";
import { setAuthToken } from "@/lib/api";
import { signIn as authSignIn, signUp as authSignUp } from "@/lib/auth";

function LoginFormInner() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState("student");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { token } = await authSignIn(email, password);
      setAuthToken(token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSignUp(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { token } = await authSignUp(email, password, name, role);
      setAuthToken(token);
      setSuccess("Account created! Redirecting...");
      setTimeout(() => router.push("/dashboard"), 1000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-surface-950 via-surface-900 to-surface-950" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(236,122,18,0.06),transparent_60%)]" />
      <div className="absolute top-1/3 left-1/3 w-72 h-72 bg-primary-500/5 rounded-full blur-3xl animate-pulse-soft" />
      <div className="absolute bottom-1/3 right-1/3 w-72 h-72 bg-accent-500/5 rounded-full blur-3xl animate-pulse-soft" style={{ animationDelay: "1s" }} />

      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 mb-4 shadow-lg shadow-primary-500/20 animate-float glow">
            <svg viewBox="0 0 32 32" fill="none" className="w-10 h-10 text-white">
              <path d="M16 4C9.373 4 4 9.373 4 16s5.373 12 12 12 12-5.373 12-12S22.627 4 16 4z" fill="currentColor" opacity="0.2" />
              <path d="M16 8c-4.418 0-8 3.582-8 8s3.582 8 8 8 8-3.582 8-8-3.582-8-8-8z" fill="currentColor" opacity="0.4" />
              <path d="M16 12c-2.209 0-4 1.791-4 4s1.791 4 4 4 4-1.791 4-4-1.791-4-4-4z" fill="currentColor" opacity="0.6" />
              <circle cx="16" cy="16" r="2" fill="currentColor" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold font-display">EduMitra AI</h1>
          <p className="text-surface-400 mt-1">Learn Better, Stress Less</p>
        </div>

        <div className="glass-strong rounded-2xl p-8 animate-slide-up">
          <div className="flex mb-6 bg-surface-800/50 rounded-lg p-1">
            <button
              onClick={() => { setMode("login"); setError(""); setSuccess(""); }}
              className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
                mode === "login" ? "bg-primary-500/20 text-primary-300 shadow-sm" : "text-surface-400 hover:text-surface-200"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setMode("signup"); setError(""); setSuccess(""); }}
              className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
                mode === "signup" ? "bg-primary-500/20 text-primary-300 shadow-sm" : "text-surface-400 hover:text-surface-200"
              }`}
            >
              Sign Up
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
              {success}
            </div>
          )}

          <form onSubmit={mode === "login" ? handleLogin : handleSignUp} className="flex flex-col gap-4">
            {mode === "signup" && (
              <input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input-premium"
                required
              />
            )}
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-premium"
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-premium"
              minLength={8}
              required
            />
            {mode === "signup" && (
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="input-premium"
              >
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
                <option value="parent">Parent</option>
              </select>
            )}
            <button type="submit" disabled={loading} className="btn-primary w-full glow">
              {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function LoadingFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-950">
      <div className="w-6 h-6 rounded-full border-2 border-primary-500/30 border-t-primary-500 animate-spin" />
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <LoginFormInner />
    </Suspense>
  );
}
