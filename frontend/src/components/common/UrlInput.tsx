"use client";

import { useState, FormEvent } from "react";

interface UrlInputProps {
  placeholder: string;
  buttonText: string;
  onSubmit: (query: string) => void;
  loading?: boolean;
}

export default function UrlInput({ placeholder, buttonText, onSubmit, loading }: UrlInputProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="input-field flex-1"
        disabled={loading}
      />
      <button type="submit" className="btn-primary whitespace-nowrap" disabled={loading || !query.trim()}>
        {loading ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Dang xu ly...
          </span>
        ) : (
          buttonText
        )}
      </button>
    </form>
  );
}
