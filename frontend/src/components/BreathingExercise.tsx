"use client";

import { useState, useEffect, useRef } from "react";

const PHASES = [
  { name: "Breathe In", duration: 4, color: "from-primary-500/30 to-accent-500/30" },
  { name: "Hold", duration: 4, color: "from-accent-500/30 to-emerald-500/30" },
  { name: "Breathe Out", duration: 4, color: "from-emerald-500/30 to-blue-500/30" },
  { name: "Hold", duration: 2, color: "from-blue-500/30 to-primary-500/30" },
];

export function BreathingExercise({ onClose }: { onClose: () => void }) {
  const [phaseIndex, setPhaseIndex] = useState(0);
  const [timeLeft, setTimeLeft] = useState(PHASES[0].duration);
  const [active, setActive] = useState(false);
  const [rounds, setRounds] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!active) return;
    intervalRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          const nextPhase = (phaseIndex + 1) % PHASES.length;
          setPhaseIndex(nextPhase);
          if (nextPhase === 0) setRounds((r) => r + 1);
          return PHASES[nextPhase].duration;
        }
        return prev - 1;
      });
    }, 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [active, phaseIndex]);

  function toggle() {
    if (!active) {
      setPhaseIndex(0);
      setTimeLeft(PHASES[0].duration);
      setRounds(0);
      setActive(true);
    } else {
      setActive(false);
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
  }

  const phase = PHASES[phaseIndex];
  const scale = phaseIndex === 0 ? 1 + timeLeft / 20 : phaseIndex === 2 ? 0.6 + (timeLeft / PHASES[2].duration) * 0.4 : 1;

  return (
    <div className="flex flex-col items-center gap-6 py-4">
      <div className="relative">
        <div
          className={`w-48 h-48 rounded-full bg-gradient-to-br ${phase.color} transition-all duration-700 flex items-center justify-center ${
            active ? "animate-pulse-glow" : ""
          }`}
          style={{ transform: `scale(${scale})` }}
        >
          <div className="w-32 h-32 rounded-full bg-surface-900/80 flex flex-col items-center justify-center backdrop-blur-sm">
            {active ? (
              <>
                <span className="text-4xl font-bold gradient-text">{timeLeft}</span>
                <span className="text-xs text-surface-400 mt-1">{phase.name}</span>
              </>
            ) : (
              <span className="text-sm text-surface-400">Press start</span>
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-2">
        {PHASES.map((p, i) => (
          <div key={p.name} className="flex flex-col items-center gap-1">
            <div
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                i === phaseIndex && active ? "bg-primary-400 scale-150" : "bg-surface-700"
              }`}
            />
          </div>
        ))}
      </div>

      <p className="text-sm text-surface-400 text-center max-w-xs">
        {active
          ? `${phase.name}${phaseIndex === 0 ? " deeply through your nose" : phaseIndex === 2 ? " slowly through your mouth" : "..."}`
          : "Find a comfortable position. Let's begin."}
      </p>

      {active && <p className="text-xs text-surface-500">Rounds completed: {rounds}</p>}

      <div className="flex gap-3">
        <button onClick={toggle} className={active ? "btn-secondary text-sm" : "btn-primary text-sm glow"}>
          {active ? "Stop" : "Start Breathing"}
        </button>
        {active && (
          <button onClick={onClose} className="btn-ghost text-sm">
            Close
          </button>
        )}
      </div>
    </div>
  );
}
