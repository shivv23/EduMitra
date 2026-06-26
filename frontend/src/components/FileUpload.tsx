"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { uploadNotes } from "@/lib/api";

export function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<{ analysis: string; summary: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const f = acceptedFiles[0];
    if (!f) return;
    setFile(f);
    setError(null);
    setResult(null);
    if (f.type.startsWith("image/")) {
      setPreview(URL.createObjectURL(f));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "image/webp": [".webp"],
      "application/pdf": [".pdf"],
    },
    maxSize: 20 * 1024 * 1024,
    maxFiles: 1,
  });

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      const data = await uploadNotes(file);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  }

  if (result) {
    return (
      <div className="glass-card p-6 animate-slide-up">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <span>✅</span> Analysis Complete
        </h3>
        <div className="p-4 rounded-xl bg-surface-800/30 mb-4">
          <p className="text-sm text-surface-200 whitespace-pre-wrap">{result.analysis}</p>
        </div>
        <div className="p-4 rounded-xl bg-accent-500/5 border border-accent-500/10">
          <p className="text-sm font-medium text-accent-400 mb-1">Summary</p>
          <p className="text-sm text-surface-300">{result.summary}</p>
        </div>
        <button onClick={() => { setFile(null); setPreview(null); setResult(null); }} className="btn-secondary text-sm mt-4">
          Upload Another
        </button>
      </div>
    );
  }

  return (
    <div className="glass-card p-6">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <span>📸</span> Upload Notes or Diagrams
      </h3>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-slide-up">
          {error}
        </div>
      )}

      {!preview ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
            isDragActive
              ? "border-primary-500/50 bg-primary-500/5 scale-[1.01]"
              : "border-surface-700/50 hover:border-surface-600 hover:bg-surface-800/30"
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-3">
            <div className="w-14 h-14 rounded-xl bg-surface-800/50 flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg className="w-7 h-7 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-surface-300">
                {isDragActive ? "Drop your file here" : "Drag & drop or click to browse"}
              </p>
              <p className="text-xs text-surface-500 mt-1">JPEG, PNG, WebP, or PDF — Max 20MB</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-4">
          <div className="relative w-full max-w-sm rounded-xl overflow-hidden border border-surface-700/50 shadow-lg">
            <img src={preview} alt="Preview" className="w-full h-auto max-h-64 object-contain bg-surface-900" />
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => { setFile(null); setPreview(null); setError(null); }} className="btn-secondary text-sm">
              Cancel
            </button>
            <button onClick={handleUpload} disabled={uploading} className="btn-primary text-sm glow">
              {uploading ? (
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Analyzing...
                </span>
              ) : "Analyze Notes"}
            </button>
          </div>
          {file && <p className="text-xs text-surface-500">{file.name} ({(file.size / 1024 / 1024).toFixed(1)} MB)</p>}
        </div>
      )}
    </div>
  );
}
