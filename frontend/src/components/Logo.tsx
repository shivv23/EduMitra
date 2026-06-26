"use client";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  animated?: boolean;
}

const sizes = { sm: "w-8 h-8", md: "w-10 h-10", lg: "w-14 h-14" };
const iconSizes = { sm: "text-sm", md: "text-lg", lg: "text-2xl" };
const textSizes = { sm: "text-lg", md: "text-xl", lg: "text-3xl" };

export function Logo({ size = "md", showText = true, animated = true }: LogoProps) {
  return (
    <div className="flex items-center gap-2.5 group">
      <div
        className={`${sizes[size]} rounded-xl bg-gradient-to-br from-primary-500 via-primary-400 to-accent-500 flex items-center justify-center text-white font-bold shadow-lg shadow-primary-500/20 ${
          animated ? "group-hover:scale-110 group-hover:shadow-primary-500/40 transition-all duration-300" : ""
        }`}
      >
        <svg viewBox="0 0 32 32" fill="none" className="w-5/6 h-5/6">
          <path d="M16 4C9.373 4 4 9.373 4 16s5.373 12 12 12 12-5.373 12-12S22.627 4 16 4z" fill="currentColor" opacity="0.2" />
          <path d="M16 8c-4.418 0-8 3.582-8 8s3.582 8 8 8 8-3.582 8-8-3.582-8-8-8z" fill="currentColor" opacity="0.4" />
          <path d="M16 12c-2.209 0-4 1.791-4 4s1.791 4 4 4 4-1.791 4-4-1.791-4-4-4z" fill="currentColor" opacity="0.6" />
          <circle cx="16" cy="16" r="2" fill="currentColor" />
          <path d="M16 2v4M16 26v4M6 6l3 3M23 23l3 3M4 16h4M24 16h4M6 26l3-3M23 9l3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
        </svg>
      </div>
      {showText && (
        <div className={`font-bold font-display ${textSizes[size]}`}>
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-300 via-primary-400 to-accent-400">
            EduMitra
          </span>
        </div>
      )}
    </div>
  );
}
