"use client";

import type { KeywordData } from "@/lib/types";

export default function GoldenKeywords({ keywords }: { keywords: KeywordData[] }) {
  const golden = keywords.filter((kw) => kw.is_golden);
  if (!golden.length) return null;

  return (
    <div className="card border-2 border-yellow-200 bg-yellow-50/50">
      <h3 className="font-semibold text-yellow-800 mb-3">Tu khoa vang (Golden Keywords)</h3>
      <p className="text-xs text-yellow-700 mb-4">High volume + Low difficulty + Commercial intent</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {golden.map((kw) => (
          <div key={kw.id} className="bg-white rounded-lg p-3 border border-yellow-200">
            <p className="font-medium text-gray-900">{kw.keyword}</p>
            <div className="flex gap-4 mt-2 text-xs text-gray-500">
              <span>Vol: {kw.search_volume?.toLocaleString()}</span>
              <span>KD: {kw.keyword_difficulty}</span>
              <span>CPC: ${kw.cpc?.toFixed(2)}</span>
              <span>Score: {kw.opportunity_score}/10</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
