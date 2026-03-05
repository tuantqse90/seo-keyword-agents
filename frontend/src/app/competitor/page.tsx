"use client";

import { useState, useCallback } from "react";
import Header from "@/components/layout/Header";
import UrlInput from "@/components/common/UrlInput";
import LoadingStream from "@/components/common/LoadingStream";
import ExportButton from "@/components/common/ExportButton";
import CompetitorCard from "@/components/competitor/CompetitorCard";
import GapMatrix from "@/components/competitor/GapMatrix";
import { useSSE } from "@/hooks/useSSE";
import { vi } from "@/i18n/vi";
import { startAnalysis, getCompetitorReport } from "@/lib/api";
import type { CompetitorData, KeywordGapData } from "@/lib/types";

export default function CompetitorPage() {
  const { content, isStreaming, error, reportId, startStream } = useSSE();
  const [competitors, setCompetitors] = useState<CompetitorData[]>([]);
  const [gaps, setGaps] = useState<KeywordGapData[]>([]);
  const [lastQuery, setLastQuery] = useState<string>("");

  const handleSubmit = useCallback(async (query: string) => {
    setLastQuery(query);
    setCompetitors([]);
    setGaps([]);
    try {
      const res = await startAnalysis("competitor", query);
      startStream(res.stream_url, res.report_id);

      const checkResults = setInterval(async () => {
        try {
          const report = await getCompetitorReport(res.report_id);
          if (report.report.status === "completed") {
            setCompetitors(report.competitors || []);
            setGaps(report.keyword_gaps || []);
            clearInterval(checkResults);
          }
        } catch {}
      }, 2000);
      setTimeout(() => clearInterval(checkResults), 120000);
    } catch (e: any) {
      console.error(e);
    }
  }, [startStream]);

  return (
    <>
      <Header title={vi.competitor.title} description={vi.competitor.description} />

      <div className="card mb-6">
        <UrlInput
          placeholder={vi.competitor.placeholder}
          buttonText={vi.competitor.analyze}
          onSubmit={handleSubmit}
          loading={isStreaming}
        />
      </div>

      <LoadingStream content={content} isStreaming={isStreaming} error={error} onRetry={lastQuery ? () => handleSubmit(lastQuery) : undefined} />

      {competitors.length > 0 && (
        <div className="space-y-6 mt-6">
          {reportId && (
            <div className="flex justify-end">
              <ExportButton reportId={reportId} />
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {competitors.map((c) => (
              <CompetitorCard key={c.id} competitor={c} />
            ))}
          </div>
          <GapMatrix gaps={gaps} />
        </div>
      )}
    </>
  );
}
