"use client";

import { useState, useCallback } from "react";
import Header from "@/components/layout/Header";
import UrlInput from "@/components/common/UrlInput";
import LoadingStream from "@/components/common/LoadingStream";
import ExportButton from "@/components/common/ExportButton";
import ScoreCard from "@/components/audit/ScoreCard";
import IssueList from "@/components/audit/IssueList";
import QuickWins from "@/components/audit/QuickWins";
import TechChecklist from "@/components/audit/TechChecklist";
import { useSSE } from "@/hooks/useSSE";
import { vi } from "@/i18n/vi";
import { startAnalysis, getAuditReport } from "@/lib/api";
import type { AuditResultData } from "@/lib/types";

export default function AuditPage() {
  const { content, isStreaming, error, reportId, startStream } = useSSE();
  const [auditResult, setAuditResult] = useState<AuditResultData | null>(null);
  const [lastQuery, setLastQuery] = useState<string>("");

  const handleSubmit = useCallback(async (query: string) => {
    setLastQuery(query);
    setAuditResult(null);
    try {
      const res = await startAnalysis("audit", query);
      startStream(res.stream_url, res.report_id);

      const checkResults = setInterval(async () => {
        try {
          const report = await getAuditReport(res.report_id);
          if (report.report.status === "completed" && report.audit_result) {
            setAuditResult(report.audit_result);
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
      <Header title={vi.audit.title} description={vi.audit.description} />

      <div className="card mb-6">
        <UrlInput
          placeholder={vi.audit.placeholder}
          buttonText={vi.audit.analyze}
          onSubmit={handleSubmit}
          loading={isStreaming}
        />
      </div>

      <LoadingStream content={content} isStreaming={isStreaming} error={error} onRetry={lastQuery ? () => handleSubmit(lastQuery) : undefined} />

      {auditResult && (
        <div className="space-y-6 mt-6">
          {reportId && (
            <div className="flex justify-end">
              <ExportButton reportId={reportId} />
            </div>
          )}
          <ScoreCard result={auditResult} />
          <QuickWins wins={auditResult.quick_wins} />
          <TechChecklist checklist={auditResult.tech_checklist} />
          <IssueList issues={auditResult.issues} />
        </div>
      )}
    </>
  );
}
