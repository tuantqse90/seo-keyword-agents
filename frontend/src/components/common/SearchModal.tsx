"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { searchReports } from "@/lib/api";
import { MODULE_COLORS } from "@/lib/constants";
import type { ReportListItem } from "@/lib/types";

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ReportListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      setQuery("");
      setResults([]);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await searchReports(query);
        setResults(data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-start justify-center pt-[10vh]">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-lg mx-4 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tim kiem bao cao..."
            className="flex-1 bg-transparent text-sm text-gray-900 dark:text-gray-100 outline-none placeholder-gray-400"
          />
          {loading && (
            <svg className="animate-spin h-4 w-4 text-gray-400" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          <kbd className="hidden sm:inline text-xs text-gray-400 border border-gray-300 dark:border-gray-600 rounded px-1.5 py-0.5">ESC</kbd>
        </div>

        <div className="max-h-[50vh] overflow-y-auto">
          {results.length > 0 ? (
            <div className="py-2">
              {results.map((r) => (
                <Link key={r.id} href={`/reports/${r.id}`} onClick={onClose}>
                  <div className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${MODULE_COLORS[r.module]}`}>
                      {r.module}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 dark:text-gray-100 truncate">{r.input_query}</p>
                      {r.summary && <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{r.summary}</p>}
                    </div>
                    <span className="text-xs text-gray-400 flex-shrink-0">
                      {new Date(r.created_at).toLocaleDateString("vi-VN")}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          ) : query.trim() && !loading ? (
            <div className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
              Khong tim thay ket qua
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
