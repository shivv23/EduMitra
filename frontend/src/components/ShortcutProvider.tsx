"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";

interface ShortcutContextType {
  searchOpen: boolean;
  setSearchOpen: (v: boolean) => void;
  shortcuts: { key: string; label: string; action: string }[];
}

const ShortcutContext = createContext<ShortcutContextType>({
  searchOpen: false,
  setSearchOpen: () => {},
  shortcuts: [],
});

export function useShortcuts() {
  return useContext(ShortcutContext);
}

export function ShortcutProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [searchOpen, setSearchOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  const shortcuts = [
    { key: "g d", label: "Go to Dashboard", action: "/dashboard" },
    { key: "g s", label: "Go to Study", action: "/study" },
    { key: "g w", label: "Go to Wellness", action: "/wellness" },
    { key: "g p", label: "Go to Progress", action: "/progress" },
    { key: "?", label: "Show shortcuts", action: "toggle" },
  ];

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "?" && !e.metaKey && !e.ctrlKey && !e.target) {
        e.preventDefault();
        setSearchOpen((p) => !p);
      }
      if (e.key === "Escape") {
        setSearchOpen(false);
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen((p) => !p);
      }
    },
    []
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return (
    <ShortcutContext.Provider value={{ searchOpen, setSearchOpen, shortcuts }}>
      {searchOpen && (
        <div className="fixed inset-0 z-[300] flex items-start justify-center pt-[15vh] p-4" onClick={() => setSearchOpen(false)}>
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
          <div
            className="relative w-full max-w-lg glass-strong rounded-2xl p-6 animate-scale-in shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Quick Navigation</h3>
              <button
                type="button"
                onClick={() => setSearchOpen(false)}
                className="w-7 h-7 rounded-lg bg-surface-800/50 hover:bg-surface-700/50 flex items-center justify-center text-surface-400 hover:text-surface-200 transition-all text-xs"
              >
                Esc
              </button>
            </div>
            <div className="flex flex-col gap-1">
              {shortcuts.map((s) => (
                <button
                  key={s.key}
                  type="button"
                  onClick={() => {
                    if (s.action !== "toggle") router.push(s.action);
                    setSearchOpen(false);
                  }}
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-surface-800/40 transition-all group"
                >
                  <span className="text-sm text-surface-300">{s.label}</span>
                  <kbd className="px-2 py-0.5 rounded-md bg-surface-800/60 text-surface-500 text-xs font-mono border border-surface-700/50 group-hover:border-primary-500/30 transition-colors">
                    {s.key}
                  </kbd>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
      {children}
      <div className="fixed bottom-4 right-4 z-40 hidden lg:block">
        <button
          type="button"
          onClick={() => setSearchOpen(true)}
          className="px-3 py-2 rounded-xl bg-surface-800/60 backdrop-blur-xl border border-surface-700/50 text-surface-500 text-xs hover:text-surface-300 hover:bg-surface-800 transition-all flex items-center gap-2 shadow-lg"
        >
          <span>⌘K</span>
          <span className="w-px h-3 bg-surface-700" />
          <span>Quick nav</span>
        </button>
      </div>
    </ShortcutContext.Provider>
  );
}
