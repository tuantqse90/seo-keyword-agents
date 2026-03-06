"use client";

import { vi } from "@/i18n/vi";
import type { CompetitorData } from "@/lib/types";

export default function CompetitorCard({ competitor }: { competitor: CompetitorData }) {
  const toArray = (val: any): string[] => {
    if (Array.isArray(val)) return val;
    if (val && typeof val === "object" && Array.isArray(val.items)) return val.items;
    return [];
  };
  const strengths = toArray(competitor.strengths);
  const weaknesses = toArray(competitor.weaknesses);
  const topKws = toArray(competitor.top_keywords);

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">{competitor.name}</h3>
          {competitor.url && (
            <p className="text-xs text-primary-600 mt-0.5">{competitor.url}</p>
          )}
        </div>
        <div className="text-right">
          {competitor.domain_authority != null && (
            <div className="text-lg font-bold text-primary-700">DA {competitor.domain_authority}</div>
          )}
        </div>
      </div>

      {competitor.estimated_traffic != null && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          {vi.competitor.traffic}: <span className="font-medium">{competitor.estimated_traffic.toLocaleString()}</span>/thang
        </p>
      )}

      {topKws.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Top Keywords</p>
          <div className="flex flex-wrap gap-1">
            {topKws.slice(0, 5).map((kw: string, i: number) => (
              <span key={i} className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-0.5 rounded-full">{kw}</span>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 mt-3">
        {strengths.length > 0 && (
          <div>
            <p className="text-xs font-medium text-green-700 dark:text-green-400 mb-1">{vi.competitor.strengths}</p>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              {strengths.map((s: string, i: number) => (
                <li key={i}>+ {s}</li>
              ))}
            </ul>
          </div>
        )}
        {weaknesses.length > 0 && (
          <div>
            <p className="text-xs font-medium text-red-700 dark:text-red-400 mb-1">{vi.competitor.weaknesses}</p>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              {weaknesses.map((w: string, i: number) => (
                <li key={i}>- {w}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
