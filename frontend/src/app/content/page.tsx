"use client";

import { useState, useCallback } from "react";
import Header from "@/components/layout/Header";
import UrlInput from "@/components/common/UrlInput";
import LoadingStream from "@/components/common/LoadingStream";
import ExportButton from "@/components/common/ExportButton";
import OutlineView from "@/components/content/OutlineView";
import MetaPreview from "@/components/content/MetaPreview";
import LsiKeywords from "@/components/content/LsiKeywords";
import { useSSE } from "@/hooks/useSSE";
import { vi } from "@/i18n/vi";
import { startAnalysis, getContentReport } from "@/lib/api";
import type { ContentBriefData } from "@/lib/types";

function EeatSignals({ signals }: { signals: any }) {
  const items: string[] = Array.isArray(signals) ? signals :
    (signals && typeof signals === "object" && Array.isArray(signals.items)) ? signals.items : [];
  if (!items.length) return null;
  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 mb-3">E-E-A-T Signals</h3>
      <ul className="space-y-1">
        {items.map((signal, i) => (
          <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
            <span className="text-green-500 mt-0.5">&#10003;</span>
            {signal}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ContentPage() {
  const { content, isStreaming, error, reportId, startStream } = useSSE();
  const [brief, setBrief] = useState<ContentBriefData | null>(null);
  const [lastQuery, setLastQuery] = useState<string>("");

  const handleSubmit = useCallback(async (query: string) => {
    setLastQuery(query);
    setBrief(null);
    try {
      const res = await startAnalysis("content", query);
      startStream(res.stream_url, res.report_id);

      const checkResults = setInterval(async () => {
        try {
          const report = await getContentReport(res.report_id);
          if (report.report.status === "completed" && report.content_brief) {
            setBrief(report.content_brief);
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
      <Header title={vi.content.title} description={vi.content.description} />

      <div className="card mb-6">
        <UrlInput
          placeholder={vi.content.placeholder}
          buttonText={vi.content.analyze}
          onSubmit={handleSubmit}
          loading={isStreaming}
        />
      </div>

      <LoadingStream content={content} isStreaming={isStreaming} error={error} onRetry={lastQuery ? () => handleSubmit(lastQuery) : undefined} />

      {brief && (
        <div className="space-y-6 mt-6">
          {reportId && (
            <div className="flex justify-end">
              <ExportButton reportId={reportId} />
            </div>
          )}
          <MetaPreview brief={brief} />
          <OutlineView outline={brief.outline} />
          <LsiKeywords keywords={brief.lsi_keywords} />

          <EeatSignals signals={brief.eeat_signals} />
        </div>
      )}
    </>
  );
}
