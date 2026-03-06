"use client";

import DataTable from "@/components/common/DataTable";
import ScoreBadge from "@/components/common/ScoreBadge";
import { vi } from "@/i18n/vi";
import type { KeywordData } from "@/lib/types";

export default function KeywordTable({ keywords }: { keywords: KeywordData[] }) {
  const columns = [
    {
      key: "keyword",
      header: vi.keywords.cluster,
      render: (kw: KeywordData) => (
        <div>
          <span className="font-medium text-gray-900 dark:text-gray-100">{kw.keyword}</span>
          {kw.is_golden && (
            <span className="ml-2 text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-0.5 rounded-full font-medium">
              {vi.keywords.golden}
            </span>
          )}
          {kw.cluster && <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{kw.cluster}</p>}
        </div>
      ),
    },
    {
      key: "search_volume",
      header: vi.keywords.volume,
      render: (kw: KeywordData) => (
        <span className="font-mono text-sm">{kw.search_volume?.toLocaleString() ?? "-"}</span>
      ),
    },
    {
      key: "keyword_difficulty",
      header: vi.keywords.difficulty,
      render: (kw: KeywordData) =>
        kw.keyword_difficulty != null ? <ScoreBadge score={kw.keyword_difficulty} /> : "-",
    },
    {
      key: "search_intent",
      header: vi.keywords.intent,
      render: (kw: KeywordData) => {
        const colors: Record<string, string> = {
          informational: "bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300",
          transactional: "bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300",
          navigational: "bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-300",
          commercial: "bg-purple-50 dark:bg-purple-900 text-purple-700 dark:text-purple-300",
        };
        return (
          <span className={`text-xs px-2 py-1 rounded-full ${colors[kw.search_intent || ""] || "bg-gray-50 dark:bg-gray-900 text-gray-500 dark:text-gray-400"}`}>
            {kw.search_intent || "-"}
          </span>
        );
      },
    },
    {
      key: "cpc",
      header: vi.keywords.cpc,
      render: (kw: KeywordData) => (
        <span className="font-mono text-sm">{kw.cpc != null ? `$${kw.cpc.toFixed(2)}` : "-"}</span>
      ),
    },
    {
      key: "opportunity_score",
      header: vi.keywords.opportunity,
      render: (kw: KeywordData) =>
        kw.opportunity_score != null ? <ScoreBadge score={kw.opportunity_score} max={10} /> : "-",
    },
  ];

  return <DataTable columns={columns} data={keywords} />;
}
