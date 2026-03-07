"use client";

import { useCallback } from "react";
import Header from "@/components/layout/Header";
import UrlInput from "@/components/common/UrlInput";
import LoadingStream from "@/components/common/LoadingStream";
import ExportButton from "@/components/common/ExportButton";
import { useSSE } from "@/hooks/useSSE";
import { useLanguage } from "@/hooks/useLanguage";
import { startWorkflow } from "@/lib/api";

export default function FixPage() {
  const { t: vi } = useLanguage();
  const { content, isStreaming, error, reportId, startStream } = useSSE();

  const handleSubmit = useCallback(async (query: string) => {
    try {
      const res = await startWorkflow("fix", query);
      startStream(res.stream_url, res.report_id);
    } catch (e: any) {
      console.error(e);
    }
  }, [startStream]);

  return (
    <>
      <Header title={vi.workflows.fix.title} description={vi.workflows.fix.description} />

      <div className="card mb-6">
        <UrlInput
          placeholder="Nhap URL can sua nhanh"
          buttonText="Kiem tra & Sua"
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
