import type { Metadata } from "next";
import "./globals.css";
import { ToastProvider } from "@/components/ToastProvider";
import { ShortcutProviderWrapper } from "@/components/ShortcutProviderWrapper";

export const metadata: Metadata = {
  title: "EduMitra AI — Learn Better, Stress Less",
  description: "Multi-Agent Personalized Learning + Mental Wellness Companion for 260 Million Indian Students",
  keywords: ["education", "AI", "tutor", "mental wellness", "Indic languages", "NCERT"],
  openGraph: {
    title: "EduMitra AI",
    description: "Learn Better, Stress Less — in your own language.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-surface-950 text-surface-50 antialiased">
        <ToastProvider />
        <ShortcutProviderWrapper>
          {children}
        </ShortcutProviderWrapper>
      </body>
    </html>
  );
}
