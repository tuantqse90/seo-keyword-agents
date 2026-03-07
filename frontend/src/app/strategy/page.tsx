"use client";

import { useCallback } from "react";
import Header from "@/components/layout/Header";
import UrlInput from "@/components/common/UrlInput";
import LoadingStream from "@/components/common/LoadingStream";
import ExportButton from "@/components/common/ExportButton";
import { useSSE } from "@/hooks/useSSE";
import { useLanguage } from "@/hooks/useLanguage";
import { startWorkflow } from "@/lib/api";

export default function StrategyPage() {
  const { t: vi } = useLanguage();
  const { content, isStreaming, error, reportId, startStream } = useSSE();

  const handleSubmit = useCallback(async (query: string) => {
    try {
      const res = await startWorkflow("strategy", query);
      startStream(res.stream_url, res.report_id);
    } catch (e: any) {
      console.error(e);
    }
  }, [startStream]);

  return (
    <>
      <Header title={vi.workflows.strategy.title} description={vi.workflows.strategy.description} />

      <div className="card mb-6">
        <UrlInput
          placeholder="Nhap URL can xay dung chien luoc"
          buttonText="Bat dau"
          onSubmit={handleSubmit}
          loading={isStreaming}
        />
      </div>

      {reportId && !isStreaming && (
        <div className="flex justify-end mb-4">
          <ExportButton reportId={reportId} />
        </div>
      )}

      <LoadingStream content={content} isStreaming={isStreaming} error={error} />
    </>
  );
}
