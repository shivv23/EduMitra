"use client";

import { useState, useRef, useCallback, useEffect } from "react";

interface VoiceRecorderProps {
  language?: string;
  onResult?: (transcript: string) => void;
}

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

const WEB_SPEECH_LANG_MAP: Record<string, string> = {
  en: "en-US",
  hi: "hi-IN",
  ta: "ta-IN",
  te: "te-IN",
  bn: "bn-IN",
  mr: "mr-IN",
  gu: "gu-IN",
  kn: "kn-IN",
  ml: "ml-IN",
  pa: "pa-IN",
  ur: "ur-PK",
};

function getSpeechRecognition() {
  if (typeof window === "undefined") return null;
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

export function VoiceRecorder({ language = "hi", onResult }: VoiceRecorderProps) {
  const [mode, setMode] = useState<"idle" | "listening" | "processing" | "result" | "unsupported">("idle");
  const [transcript, setTranscript] = useState("");
  const [interimText, setInterimText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  const hasWebSpeech = typeof window !== "undefined" && !!getSpeechRecognition();

  useEffect(() => {
    if (!hasWebSpeech) setMode("unsupported");
  }, [hasWebSpeech]);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch {}
      }
    };
  }, []);

  const startListening = useCallback(() => {
    setError(null);
    setTranscript("");
    setInterimText("");

    if (!hasWebSpeech) {
      setMode("unsupported");
      return;
    }

    try {
      const SpeechRecognition = getSpeechRecognition();
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      recognition.lang = WEB_SPEECH_LANG_MAP[language] || "hi-IN";
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setMode("listening");

      recognition.onresult = (event: any) => {
        let final = "";
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }
        if (final) setTranscript((prev) => prev + final);
        setInterimText(interim);
      };

      recognition.onerror = (event: any) => {
        if (event.error === "no-speech") {
          setError("No speech detected. Please try again.");
        } else if (event.error === "audio-capture") {
          setError("Microphone not found. Please check your mic.");
        } else if (event.error === "not-allowed") {
          setError("Microphone access denied. Allow mic permission in your browser.");
        } else {
          setError(`Speech recognition error: ${event.error}`);
        }
        setMode("idle");
      };

      recognition.onend = () => {
        setMode(transcript ? "result" : "idle");
        setInterimText("");
      };

      recognition.start();
    } catch (e) {
      setError("Failed to start speech recognition.");
      setMode("idle");
    }
  }, [language, hasWebSpeech, transcript]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
    }
    if (transcript) {
      setMode("result");
    } else {
      setMode("idle");
    }
    setInterimText("");
  }, [transcript]);

  const handleUseTranscript = useCallback(() => {
    if (transcript) {
      onResult?.(transcript);
    }
  }, [transcript, onResult]);

  if (mode === "unsupported") {
    return (
      <div className="glass-card p-6 bg-gradient-to-br from-amber-500/5 to-orange-500/5">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <span>🎤</span> Voice Input
          <span className="text-xs font-normal text-surface-500 ml-1">(fallback mode)</span>
        </h3>
        <p className="text-sm text-surface-400 mb-3">
          Your browser doesn't support the Web Speech API. Use Chrome/Edge for voice typing.
        </p>
        <p className="text-xs text-surface-500">
          Try the MediaRecorder option below, or type your question directly in the chat.
        </p>
      </div>
    );
  }

  const displayText = transcript + (interimText ? ` ${interimText}` : "");

  return (
    <div className="glass-card p-6 bg-gradient-to-br from-primary-500/5 to-accent-500/5">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <span>🎤</span> Voice Input
        <span className="text-xs font-normal text-surface-500 ml-1">
          ({WEB_SPEECH_LANG_MAP[language] || "hi-IN"})
        </span>
      </h3>

      {error && (
        <div className="mb-3 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-slide-up flex items-center gap-2">
          <span>⚠️</span>
          <span className="flex-1">{error}</span>
          <button onClick={() => setError(null)} className="text-red-400/60 hover:text-red-400">✕</button>
        </div>
      )}

      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={mode === "listening" ? stopListening : startListening}
          className={`w-16 h-16 rounded-full flex items-center justify-center text-white text-xl transition-all duration-200 ${
            mode === "listening"
              ? "bg-red-500 hover:bg-red-400 animate-pulse shadow-lg shadow-red-500/30 scale-110"
              : "bg-gradient-to-br from-primary-500 to-accent-500 hover:scale-110 shadow-lg shadow-primary-500/20"
          } active:scale-95`}
          title={mode === "listening" ? "Stop listening" : "Start voice input"}
        >
          {mode === "listening" ? (
            <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="4" width="4" height="16" rx="1" />
              <rect x="14" y="4" width="4" height="16" rx="1" />
            </svg>
          ) : (
            <svg className="w-7 h-7 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14a4 4 0 004-4V6a4 4 0 00-8 0v4a4 4 0 004 4z" />
              <path d="M19 11a7 7 0 01-14 0H3a9 9 0 0018 0h-2z" />
            </svg>
          )}
        </button>

        <div className="flex-1 min-h-[48px] flex items-center">
          {mode === "listening" ? (
            <div className="flex flex-col gap-1 w-full">
              {displayText ? (
                <div className="text-sm text-surface-200 bg-surface-800/30 rounded-xl p-3 w-full animate-fade-in">
                  {displayText}
                  <span className="inline-block w-0.5 h-4 bg-primary-400 animate-pulse ml-0.5 align-middle" />
                </div>
              ) : (
                <div className="flex items-center gap-3 text-sm text-primary-400">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-primary-500" />
                  </span>
                  Listening... speak now
                  <span className="text-primary-400/60 text-xs">(tap mic to stop)</span>
                </div>
              )}
            </div>
          ) : transcript ? (
            <div className="text-sm text-surface-200 bg-surface-800/30 rounded-xl p-3 w-full animate-fade-in">
              <p className="text-xs text-accent-400 mb-1 flex items-center gap-1">
                <span>✓</span> Transcribed
              </p>
              {transcript}
            </div>
          ) : (
            <div className="text-sm text-surface-400">
              <p>Tap the mic and speak your question.</p>
              <p className="text-xs text-surface-500 mt-0.5">
                Real-time transcription — tap again to stop.
              </p>
            </div>
          )}
        </div>
      </div>

      {transcript && mode === "result" && (
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={() => {
              setTranscript("");
              setError(null);
              setMode("idle");
            }}
            className="btn-ghost text-xs"
          >
            Clear
          </button>
          <button
            type="button"
            onClick={handleUseTranscript}
            className="btn-primary text-xs py-2 glow"
          >
            Send to Chat →
          </button>
        </div>
      )}
    </div>
  );
}


export function SpeakButton({ text }: { text: string }) {
  const [speaking, setSpeaking] = useState(false);

  const speak = useCallback(() => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "hi-IN";
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  }, [text, speaking]);

  return (
    <button
      type="button"
      onClick={speak}
      className={`p-1.5 rounded-lg transition-all active:scale-90 ${
        speaking
          ? "bg-accent-500/20 text-accent-300"
          : "text-surface-500 hover:text-surface-300 hover:bg-surface-800/50"
      }`}
      title={speaking ? "Stop" : "Read aloud"}
    >
      {speaking ? (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <rect x="6" y="4" width="4" height="16" rx="1" />
          <rect x="14" y="4" width="4" height="16" rx="1" />
        </svg>
      ) : (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
        </svg>
      )}
    </button>
  );
}
