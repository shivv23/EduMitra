import { SUPPORTED_LANGUAGES } from "@/types";

export function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}

export function formatDate(date: Date | string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

export function formatTime(date: Date | string) {
  return new Intl.DateTimeFormat("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function timeAgo(date: Date | string) {
  const now = new Date();
  const d = new Date(date);
  const seconds = Math.floor((now.getTime() - d.getTime()) / 1000);

  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return formatDate(date);
}

export function getLanguageName(code: string) {
  return SUPPORTED_LANGUAGES.find((l) => l.code === code)?.native || code;
}

export function masteryColor(score: number) {
  if (score >= 80) return "from-accent-500 to-emerald-400";
  if (score >= 60) return "from-primary-500 to-accent-500";
  if (score >= 40) return "from-amber-500 to-orange-500";
  return "from-red-500 to-rose-500";
}

export function masteryLabel(score: number) {
  if (score >= 80) return "Excellent";
  if (score >= 60) return "Good";
  if (score >= 40) return "Needs Work";
  return "Struggling";
}
