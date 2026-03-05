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
          <span className="font-medium text-gray-900">{kw.keyword}</span>
          {kw.is_golden && (
            <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full font-medium">
              {vi.keywords.golden}
            </span>
          )}
          {kw.cluster && <p className="text-xs text-gray-400 mt-0.5">{kw.cluster}</p>}
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
          informational: "bg-blue-50 text-blue-700",
          transactional: "bg-green-50 text-green-700",
          navigational: "bg-gray-50 text-gray-700",
          commercial: "bg-purple-50 text-purple-700",
        };
        return (
          <span className={`text-xs px-2 py-1 rounded-full ${colors[kw.search_intent || ""] || "bg-gray-50 text-gray-500"}`}>
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
