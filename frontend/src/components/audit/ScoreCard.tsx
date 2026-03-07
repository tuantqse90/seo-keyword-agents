"use client";

import { useLanguage } from "@/hooks/useLanguage";
import type { AuditResultData } from "@/lib/types";

export default function ScoreCard({ result }: { result: AuditResultData }) {
  const { t: vi } = useLanguage();
  const score = result.overall_score ?? 0;
  const pct = score;
  const color = pct >= 80 ? "text-green-600" : pct >= 60 ? "text-yellow-600" : pct >= 40 ? "text-orange-600" : "text-red-600";
  const ringColor = pct >= 80 ? "stroke-green-500" : pct >= 60 ? "stroke-yellow-500" : pct >= 40 ? "stroke-orange-500" : "stroke-red-500";

  const critical = result.issues.filter((i) => i.severity === "Critical").length;
  const warning = result.issues.filter((i) => i.severity === "Warning").length;
  const info = result.issues.filter((i) => i.severity === "Info").length;

  return (
    <div className="card flex items-center gap-8">
      <div className="relative w-28 h-28">
        <svg className="w-28 h-28 -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" strokeWidth="8" />
          <circle
            cx="50" cy="50" r="45" fill="none"
            className={ringColor}
            strokeWidth="8"
            strokeDasharray={`${pct * 2.83} ${283 - pct * 2.83}`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-2xl font-bold ${color}`}>{score}</span>
          <span className="text-xs text-gray-400 dark:text-gray-500">/100</span>
        </div>
      </div>

      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl font-bold text-gray-900 dark:text-gray-100">{vi.audit.grade}:</span>
          <span className={`text-2xl font-bold ${color}`}>{result.letter_grade || "N/A"}</span>
        </div>
        <div className="flex gap-4 text-sm">
          <span className="text-red-600">{critical} {vi.audit.critical}</span>
          <span className="text-yellow-600">{warning} {vi.audit.warning}</span>
          <span className="text-blue-600">{info} {vi.audit.info}</span>
        </div>
      </div>
    </div>
  );
}
