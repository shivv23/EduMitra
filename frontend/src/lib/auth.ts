const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://edumitra-ai.onrender.com";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: "student" | "teacher" | "parent" | "admin";
}

const TOKEN_KEY = "edumitra_token";
const USER_KEY = "edumitra_user";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearSession() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function authRequest<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(10000),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Authentication failed");
  return data;
}

export async function signIn(email: string, password: string): Promise<{ token: string; user: AuthUser }> {
  const data = await authRequest<{ token: string; user: AuthUser }>("/api/auth/signin", { email, password });
  localStorage.setItem(TOKEN_KEY, data.token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  return data;
}

export async function signUp(
  email: string,
  password: string,
  name: string,
  role: string
): Promise<{ token: string; user: AuthUser }> {
  const data = await authRequest<{ token: string; user: AuthUser }>("/api/auth/signup", {
    email,
    password,
    name,
    role,
  });
  localStorage.setItem(TOKEN_KEY, data.token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  return data;
}

export function signOut() {
  clearSession();
  window.location.href = "/login";
}
