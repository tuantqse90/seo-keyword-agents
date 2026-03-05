"use client";

import type { KeywordData } from "@/lib/types";

export default function ClusterView({ keywords }: { keywords: KeywordData[] }) {
  const clusters: Record<string, KeywordData[]> = {};
  for (const kw of keywords) {
    const cluster = kw.cluster || "Khac";
    if (!clusters[cluster]) clusters[cluster] = [];
    clusters[cluster].push(kw);
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Object.entries(clusters).map(([name, kws]) => (
        <div key={name} className="card">
          <h3 className="font-semibold text-gray-900 mb-3">{name}</h3>
          <div className="space-y-2">
            {kws.map((kw) => (
              <div key={kw.id} className="flex items-center justify-between text-sm">
                <span className="text-gray-700">{kw.keyword}</span>
                <span className="text-gray-400 font-mono text-xs">
                  {kw.search_volume?.toLocaleString() ?? "?"}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
