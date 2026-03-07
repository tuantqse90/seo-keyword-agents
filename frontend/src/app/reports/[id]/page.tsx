"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import Header from "@/components/layout/Header";
import ExportButton from "@/components/common/ExportButton";
import { getReport } from "@/lib/api";
import { MODULE_COLORS, STATUS_COLORS } from "@/lib/constants";
import { useLanguage } from "@/hooks/useLanguage";
import type { Report } from "@/lib/types";

export default function ReportDetailPage() {
  const { t: vi } = useLanguage();
  const params = useParams();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      getReport(params.id as string)
        .then(setReport)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [params.id]);

  if (loading) {
    return <div className="text-center py-12 text-gray-500 dark:text-gray-400">{vi.common.loading}</div>;
  }

  if (!report) {
    return <div className="text-center py-12 text-gray-500 dark:text-gray-400">Khong tim thay bao cao</div>;
  }

  return (
    <>
      <Header title={`Bao cao: ${report.input_query}`} />

      <div className="flex items-center gap-3 mb-6">
        <span className={`text-sm px-3 py-1 rounded-full font-medium ${MODULE_COLORS[report.module]}`}>
          {report.module}
        </span>
        <span className={`text-sm px-3 py-1 rounded-full ${STATUS_COLORS[report.status]}`}>
          {vi.common.status[report.status as keyof typeof vi.common.status]}
        </span>
        <span className="text-sm text-gray-400 dark:text-gray-500">
          {new Date(report.created_at).toLocaleString("vi-VN")}
        </span>
        <div className="flex-1" />
        <ExportButton reportId={report.id} />
      </div>

      {report.summary && (
        <div className="card mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Tom tat</h3>
          <p className="text-gray-700 dark:text-gray-300">{report.summary}</p>
        </div>
      )}

      {report.raw_markdown && (
        <div className="card">
          <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:text-gray-900 dark:prose-headings:text-gray-100 prose-p:text-gray-700 dark:prose-p:text-gray-300">
            <ReactMarkdown>{report.raw_markdown}</ReactMarkdown>
          </div>
        </div>
      )}
    </>
  );
}
