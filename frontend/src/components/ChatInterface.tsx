"use client";

import { useState, useRef, useEffect } from "react";
import type { Message } from "@/types";
import { sendChatMessage } from "@/lib/api";
import { formatTime } from "@/lib/utils";
import { SpeakButton } from "@/components/VoiceRecorder";

function TypingIndicator() {
  return (
    <div className="flex justify-start message-enter">
      <div className="glass rounded-2xl rounded-bl-md p-4">
        <div className="flex gap-1.5">
          <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: "0ms" }} />
          <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: "150ms" }} />
          <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}

function ChatMessage({ msg }: { msg: Message }) {
  return (
    <div className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} message-enter`}>
      <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 ${
        msg.role === "user"
          ? "bg-gradient-to-br from-primary-600/80 to-primary-500/80 text-white rounded-br-md shadow-lg shadow-primary-500/10"
          : "glass rounded-bl-md"
      }`}>
        <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
        <p className={`text-xs mt-2 flex items-center gap-1 ${msg.role === "user" ? "text-primary-200" : "text-surface-500"}`}>
          {msg.type === "image" && <span>📸</span>}
          {msg.type === "audio" && <span>🎤</span>}
          {msg.timestamp instanceof Date ? formatTime(msg.timestamp) : formatTime(new Date(msg.timestamp))}
          {msg.role === "assistant" && <SpeakButton text={msg.content} />}
        </p>
      </div>
    </div>
  );
}

interface ChatInterfaceProps {
  onUploadClick?: () => void;
  externalText?: string;
}

export function ChatInterface({ onUploadClick, externalText }: ChatInterfaceProps) {
  useEffect(() => {
    if (externalText) setInput(externalText);
  }, [externalText]);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Namaste! I'm your EduMitra AI tutor. I can help you with:\n\n• 📚 **Study questions** — Explain any topic\n• 📸 **Notes upload** — Analyze handwritten notes\n• 🧠 **Wellness check** — Talk about how you're feeling\n• 🗣️ **Voice support** — Get answers in your language\n\nWhat would you like to learn today?",
      timestamp: new Date(),
      type: "text",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || isLoading) return;

    const text = input.trim();
    setInput("");

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date(),
      type: "text",
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const recentHistory = messages
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }));
      const result = await sendChatMessage(text, recentHistory);

      const assistantMessage: Message = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: result.response,
        timestamp: new Date(),
        type: (result.type as Message["type"]) || "text",
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: err instanceof Error
          ? `I'm having trouble connecting. ${err.message}`
          : "I'm having trouble connecting to my knowledge base. Please try again in a moment.",
        timestamp: new Date(),
        type: "text",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} msg={msg} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-surface-800/50 p-4 bg-surface-950/50">
        <div className="flex items-end gap-3 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your studies..."
              rows={1}
              className="input-premium resize-none pr-12 py-3.5 min-h-[48px] max-h-32"
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = "auto";
                target.style.height = `${Math.min(target.scrollHeight, 128)}px`;
              }}
            />
            <button
              onClick={onUploadClick}
              className="absolute right-3 bottom-3 p-1.5 rounded-lg hover:bg-surface-700/50 text-surface-400 hover:text-surface-200 transition-colors active:scale-90"
              title="Upload image"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="btn-primary px-4 py-3 rounded-xl disabled:opacity-40 glow active:scale-95 transition-transform"
          >
            {isLoading ? (
              <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-6" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
