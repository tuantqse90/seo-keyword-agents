"use client";

import type { KeywordGapData } from "@/lib/types";
import { useLanguage } from "@/hooks/useLanguage";

export default function GapMatrix({ gaps }: { gaps: KeywordGapData[] }) {
  const { t: vi } = useLanguage();
  if (!gaps.length) return null;

  const allCompetitors = new Set<string>();
  gaps.forEach((g) => {
    if (g.competitor_ranks) {
      Object.keys(g.competitor_ranks).forEach((c) => allCompetitors.add(c));
    }
  });
  const competitors = Array.from(allCompetitors);

  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">{vi.competitor.gaps}</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left py-2 px-3 text-gray-600 dark:text-gray-400 font-medium">Keyword</th>
              <th className="text-center py-2 px-3 text-gray-600 dark:text-gray-400 font-medium">Ban</th>
              {competitors.map((c) => (
                <th key={c} className="text-center py-2 px-3 text-gray-600 dark:text-gray-400 font-medium">{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {gaps.map((gap) => (
              <tr key={gap.id} className="border-b border-gray-100 dark:border-gray-700">
                <td className="py-2 px-3 font-medium">{gap.keyword}</td>
                <td className="py-2 px-3 text-center">
                  {gap.target_rank ? (
                    <span className="font-mono">{gap.target_rank}</span>
                  ) : (
                    <span className="text-red-500">-</span>
                  )}
                </td>
                {competitors.map((c) => (
                  <td key={c} className="py-2 px-3 text-center font-mono">
                    {gap.competitor_ranks?.[c] ?? "-"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
