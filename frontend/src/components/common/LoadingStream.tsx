"use client";

import ReactMarkdown from "react-markdown";
import { vi } from "@/i18n/vi";

interface LoadingStreamProps {
  content: string;
  isStreaming: boolean;
  error: string | null;
  onRetry?: () => void;
}

export default function LoadingStream({ content, isStreaming, error, onRetry }: LoadingStreamProps) {
  if (error) {
    return (
      <div className="card border-red-200 bg-red-50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-red-700 font-medium">{vi.common.error}</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
          </div>
          {onRetry && (
            <button onClick={onRetry} className="btn-primary text-sm">
              {vi.common.retry}
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!content && !isStreaming) return null;

  return (
    <div className="card">
      {isStreaming && (
        <div className="flex items-center gap-2 mb-4 text-primary-600">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span className="text-sm font-medium">{vi.common.streaming}</span>
        </div>
      )}
      <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-table:text-sm dark:prose-invert">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
      {isStreaming && (
        <span className="inline-block w-2 h-5 bg-primary-500 animate-pulse ml-1" />
      )}
    </div>
  );
}
