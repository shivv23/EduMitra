"use client";

import { useState, useRef, useCallback } from "react";
import { sendAudioMessage } from "@/lib/api";

interface VoicePlayerProps {
  language?: string;
  onResult?: (transcript: string) => void;
}

export function VoicePlayer({ language = "hi", onResult }: VoicePlayerProps) {
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    setError(null);
    setTranscript(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        if (blob.size === 0) return;

        setProcessing(true);
        try {
          const result = await sendAudioMessage(blob);
          if (result.transcript) {
            setTranscript(result.transcript);
            onResult?.(result.transcript);
          }
        } catch {
          setError("Could not process audio. Please try again.");
        } finally {
          setProcessing(false);
        }
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setRecording(true);
    } catch {
      setError("Microphone access denied. Please allow microphone permissions.");
    }
  }, [onResult]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  }, []);

  return (
    <div className="glass-card p-6 bg-gradient-to-br from-blue-500/5 to-cyan-500/5">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <span>🎤</span> Voice Input
        <span className="text-xs font-normal text-surface-500 ml-1">
          ({language === "hi" ? "Hindi" : language === "ta" ? "Tamil" : language === "te" ? "Telugu" : language === "bn" ? "Bengali" : language === "mr" ? "Marathi" : language === "gu" ? "Gujarati" : language === "kn" ? "Kannada" : language === "ml" ? "Malayalam" : language === "pa" ? "Punjabi" : language === "ur" ? "Urdu" : "English"})
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
          onClick={recording ? stopRecording : startRecording}
          disabled={processing}
          className={`w-16 h-16 rounded-full flex items-center justify-center text-white text-xl transition-all duration-200 ${
            recording
              ? "bg-red-500 hover:bg-red-400 animate-pulse shadow-lg shadow-red-500/30 scale-110"
              : "bg-gradient-to-br from-primary-500 to-accent-500 hover:scale-110 shadow-lg shadow-primary-500/20"
          } active:scale-95 disabled:opacity-50`}
          title={recording ? "Stop recording" : "Start recording"}
        >
          {processing ? (
            <svg className="w-7 h-7 animate-spin" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : recording ? (
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
          {processing ? (
            <div className="flex items-center gap-3 text-sm text-surface-400">
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
              Processing your voice...
            </div>
          ) : transcript ? (
            <div className="text-sm text-surface-200 bg-surface-800/30 rounded-xl p-3 w-full animate-fade-in">
              <p className="text-xs text-accent-400 mb-1 flex items-center gap-1">
                <span>✓</span> Transcribed
              </p>
              {transcript}
            </div>
          ) : recording ? (
            <div className="flex items-center gap-3 text-sm text-red-400">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
              </span>
              Recording... tap to stop
            </div>
          ) : (
            <div className="text-sm text-surface-400">
              <p>Tap the mic to ask a question with your voice.</p>
              <p className="text-xs text-surface-500 mt-0.5">Supports {language === "hi" ? "Hindi" : "Indian languages"} — transcript appears here.</p>
            </div>
          )}
        </div>
      </div>

      {transcript && (
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={() => {
              setTranscript(null);
              setError(null);
            }}
            className="btn-ghost text-xs"
          >
            Clear
          </button>
          <button
            type="button"
            onClick={() => {
              if (transcript) onResult?.(transcript);
            }}
            className="btn-primary text-xs py-2 glow"
          >
            Use in Chat →
          </button>
        </div>
      )}
    </div>
  );
}
