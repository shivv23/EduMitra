"use client";

import { useState } from "react";
import { fetchQuiz } from "@/lib/api";

interface Question {
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

export function QuizCard({ topic }: { topic?: string }) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function startQuiz() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchQuiz(topic);
      setQuestions(data.questions);
      setCurrentQ(0);
      setSelected(null);
      setShowResult(false);
      setScore(0);
    } catch {
      setError("Could not load quiz. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="glass-card p-6">
        <div className="skeleton h-5 w-32 mb-4" />
        <div className="skeleton h-4 w-full mb-4" />
        <div className="skeleton h-10 w-full mb-2" />
        <div className="skeleton h-10 w-full mb-2" />
        <div className="skeleton h-10 w-full mb-2" />
        <div className="skeleton h-10 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-6 text-center">
        <p className="text-surface-400 text-sm mb-3">{error}</p>
        <button onClick={startQuiz} className="btn-secondary text-sm">Try Again</button>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="glass-card p-6 text-center">
        <p className="text-2xl mb-2">📝</p>
        <h3 className="font-semibold mb-1">Ready for a Quiz?</h3>
        <p className="text-sm text-surface-400 mb-4">Test your knowledge with a quick quiz.</p>
        <button onClick={startQuiz} className="btn-primary text-sm glow">Start Quiz</button>
      </div>
    );
  }

  const q = questions[currentQ];
  const isLast = currentQ === questions.length - 1;

  function handleAnswer(index: number) {
    setSelected(index);
    setShowResult(true);
    if (index === q.correctAnswer) setScore((s) => s + 1);
  }

  function nextQuestion() {
    if (!isLast) {
      setCurrentQ((c) => c + 1);
      setSelected(null);
      setShowResult(false);
    }
  }

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Quick Quiz</h3>
        <span className="badge-primary">{currentQ + 1}/{questions.length}</span>
      </div>

      <p className="text-sm font-medium text-surface-200 mb-4">{q.question}</p>

      <div className="flex flex-col gap-2">
        {q.options.map((opt, i) => {
          let classes = "p-3 rounded-xl text-sm text-left transition-all border ";
          if (!showResult) {
            classes += "bg-surface-800/30 border-surface-700/30 hover:bg-surface-800/60 hover:border-surface-600/50 cursor-pointer";
          } else if (i === q.correctAnswer) {
            classes += "bg-accent-500/10 border-accent-500/30 text-accent-300";
          } else if (i === selected) {
            classes += "bg-red-500/10 border-red-500/30 text-red-300";
          } else {
            classes += "bg-surface-800/30 border-surface-700/30 opacity-50";
          }

          return (
            <button key={i} onClick={() => !showResult && handleAnswer(i)} disabled={showResult} className={classes}>
              <span className="text-surface-500 mr-2">{String.fromCharCode(65 + i)}.</span>
              {opt}
            </button>
          );
        })}
      </div>

      {showResult && (
        <div className="mt-4 p-3 rounded-xl bg-surface-800/30 text-sm text-surface-300 animate-fade-in">
          <p className="font-medium text-accent-400 mb-1">
            {selected === q.correctAnswer ? "Correct! ✓" : "Not quite. Here's why:"}
          </p>
          <p className="text-surface-400">{q.explanation}</p>
        </div>
      )}

      {showResult && !isLast && (
        <button onClick={nextQuestion} className="btn-primary w-full mt-4 text-sm glow">
          Next Question
        </button>
      )}

      {isLast && showResult && (
        <div className="mt-4 p-4 rounded-xl bg-gradient-to-br from-primary-500/10 to-accent-500/10 text-center animate-fade-in">
          <p className="text-2xl font-bold gradient-text">{score}/{questions.length}</p>
          <p className="text-sm text-surface-400 mt-1">Quiz Complete! Great effort.</p>
          <button onClick={startQuiz} className="btn-secondary text-sm mt-3">Try Another Quiz</button>
        </div>
      )}
    </div>
  );
}
