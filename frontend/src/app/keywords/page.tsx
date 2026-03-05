"use client";

import { useState, useCallback } from "react";
import Header from "@/components/layout/Header";
import UrlInput from "@/components/common/UrlInput";
import LoadingStream from "@/components/common/LoadingStream";
import ExportButton from "@/components/common/ExportButton";
import KeywordTable from "@/components/keywords/KeywordTable";
import ClusterView from "@/components/keywords/ClusterView";
import GoldenKeywords from "@/components/keywords/GoldenKeywords";
import { useSSE } from "@/hooks/useSSE";
import { vi } from "@/i18n/vi";
import { startAnalysis, getKeywordReport } from "@/lib/api";
import type { KeywordData } from "@/lib/types";

export default function KeywordsPage() {
  const { content, isStreaming, error, reportId, startStream } = useSSE();
  const [keywords, setKeywords] = useState<KeywordData[]>([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<"table" | "cluster">("table");
  const [lastQuery, setLastQuery] = useState<string>("");

  const handleSubmit = useCallback(async (query: string) => {
    setLastQuery(query);
    setLoading(true);
    setKeywords([]);
    try {
      const res = await startAnalysis("keywords", query);
      startStream(res.stream_url, res.report_id);

      // Poll for results after stream
      const checkResults = setInterval(async () => {
        try {
          const report = await getKeywordReport(res.report_id);
          if (report.report.status === "completed" && report.keywords.length > 0) {
            setKeywords(report.keywords);
            clearInterval(checkResults);
          }
        } catch {}
      }, 2000);

      setTimeout(() => clearInterval(checkResults), 120000);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [startStream]);

  return (
    <>
      <Header title={vi.keywords.title} description={vi.keywords.description} />

      <div className="card mb-6">
        <UrlInput
          placeholder={vi.keywords.placeholder}
          buttonText={vi.keywords.analyze}
          onSubmit={handleSubmit}
          loading={isStreaming}
        />
      </div>

      <LoadingStream content={content} isStreaming={isStreaming} error={error} onRetry={lastQuery ? () => handleSubmit(lastQuery) : undefined} />

      {keywords.length > 0 && (
        <div className="space-y-6 mt-6">
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              <button
                onClick={() => setView("table")}
                className={view === "table" ? "btn-primary text-sm" : "btn-secondary text-sm"}
              >
                Bang du lieu
              </button>
              <button
                onClick={() => setView("cluster")}
                className={view === "cluster" ? "btn-primary text-sm" : "btn-secondary text-sm"}
              >
                Nhom tu khoa
              </button>
            </div>
            {reportId && <ExportButton reportId={reportId} />}
          </div>

          <GoldenKeywords keywords={keywords} />

          {view === "table" ? (
            <div className="card">
              <KeywordTable keywords={keywords} />
            </div>
          ) : (
            <ClusterView keywords={keywords} />
          )}
        </div>
      )}
    </>
  );
}
