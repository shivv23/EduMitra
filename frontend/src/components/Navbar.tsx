"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut } from "@/lib/auth";
import { useState, useEffect, useRef } from "react";
import { Logo } from "./Logo";

interface NavbarProps {
  userName?: string;
  userRole?: string;
  avatarUrl?: string;
}

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard", roles: ["student", "parent", "teacher", "admin"] },
  { href: "/study", label: "Study", roles: ["student"] },
  { href: "/wellness", label: "Wellness", roles: ["student"] },
  { href: "/progress", label: "Progress", roles: ["student", "parent"] },
  { href: "/parent", label: "Parent View", roles: ["parent"] },
  { href: "/teacher", label: "Teacher View", roles: ["teacher", "admin"] },
];

export default function Navbar({ userName, userRole, avatarUrl }: NavbarProps) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const visibleLinks = NAV_LINKS.filter((l) => l.roles.includes(userRole || "student"));

  return (
    <nav className="sticky top-0 z-50 border-b border-surface-800/50 bg-surface-950/80 backdrop-blur-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            <Logo size="sm" animated />
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {visibleLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  pathname.startsWith(link.href)
                    ? "bg-primary-500/10 text-primary-300 border border-primary-500/20"
                    : "text-surface-400 hover:text-surface-200 hover:bg-surface-800/50"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3" ref={menuRef}>
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 p-1.5 pr-3 rounded-xl hover:bg-surface-800/50 transition-all active:scale-95"
            >
              {avatarUrl ? (
                <img src={avatarUrl} alt="" className="w-8 h-8 rounded-full object-cover ring-2 ring-primary-500/20" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-xs font-bold ring-2 ring-primary-500/20">
                  {userName?.charAt(0)?.toUpperCase() || "S"}
                </div>
              )}
              <div className="text-sm hidden sm:block text-left">
                <p className="text-surface-200 font-medium leading-tight truncate max-w-[120px]">{userName || "Student"}</p>
                <p className="text-surface-500 text-xs capitalize">{userRole || "student"}</p>
              </div>
              <svg className={`w-3.5 h-3.5 text-surface-500 transition-transform duration-200 ${userMenuOpen ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {userMenuOpen && (
              <div className="absolute top-16 right-4 w-56 glass-strong rounded-xl py-2 animate-slide-up shadow-2xl border border-surface-700/50">
                <div className="px-4 py-3 border-b border-surface-800/50">
                  <p className="text-sm font-medium text-surface-200">{userName}</p>
                  <p className="text-xs text-surface-500 capitalize">{userRole}</p>
                </div>
                <div className="py-1">
                  {visibleLinks.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      onClick={() => setUserMenuOpen(false)}
                      className={`flex items-center gap-2 px-4 py-2.5 text-sm transition-colors ${
                        pathname.startsWith(link.href)
                          ? "text-primary-300 bg-primary-500/5"
                          : "text-surface-400 hover:text-surface-200 hover:bg-surface-800/30"
                      }`}
                    >
                      {link.href === "/dashboard" && "📊"}
                      {link.href === "/study" && "📚"}
                      {link.href === "/wellness" && "🧠"}
                      {link.href === "/progress" && "📈"}
                      {link.href === "/parent" && "👨‍👩‍👧"}
                      {link.href === "/teacher" && "👩‍🏫"}
                      {link.label}
                    </Link>
                  ))}
                </div>
                <div className="border-t border-surface-800/50 pt-1">
                  <form action={signOut}>
                    <button type="submit" className="w-full text-left px-4 py-2.5 text-sm text-surface-400 hover:text-red-400 hover:bg-surface-800/30 transition-colors flex items-center gap-2">
                      <span>🚪</span> Sign Out
                    </button>
                  </form>
                </div>
              </div>
            )}

            <button
              className="md:hidden p-2 rounded-lg hover:bg-surface-800/50 text-surface-400 active:scale-95 transition-all"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Toggle menu"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {menuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="md:hidden py-3 border-t border-surface-800/50 animate-slide-up stagger-children">
            {visibleLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMenuOpen(false)}
                className={`block px-4 py-2.5 rounded-lg text-sm font-medium mb-1 ${
                  pathname.startsWith(link.href)
                    ? "bg-primary-500/10 text-primary-300"
                    : "text-surface-400 hover:text-surface-200 hover:bg-surface-800/30"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
