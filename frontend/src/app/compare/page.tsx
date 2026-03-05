"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import Header from "@/components/layout/Header";
import { vi } from "@/i18n/vi";
import { getReports, getReport } from "@/lib/api";
import { MODULE_COLORS } from "@/lib/constants";
import type { ReportListItem, Report } from "@/lib/types";

export default function ComparePage() {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [leftId, setLeftId] = useState<string>("");
  const [rightId, setRightId] = useState<string>("");
  const [leftReport, setLeftReport] = useState<Report | null>(null);
  const [rightReport, setRightReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getReports({ limit: "100" })
      .then((data) => setReports(data.filter((r: ReportListItem) => r.status === "completed")))
      .catch(() => []);
  }, []);

  useEffect(() => {
    if (leftId) {
      getReport(leftId).then(setLeftReport).catch(() => setLeftReport(null));
    } else {
      setLeftReport(null);
    }
  }, [leftId]);

  useEffect(() => {
    if (rightId) {
      getReport(rightId).then(setRightReport).catch(() => setRightReport(null));
    } else {
      setRightReport(null);
    }
  }, [rightId]);

  const ReportSelector = ({
    value,
    onChange,
    excludeId,
  }: {
    value: string;
    onChange: (v: string) => void;
    excludeId: string;
  }) => (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
    >
      <option value="">-- Chon bao cao --</option>
      {reports
        .filter((r) => r.id !== excludeId)
        .map((r) => (
          <option key={r.id} value={r.id}>
            [{r.module}] {r.input_query} — {new Date(r.created_at).toLocaleDateString("vi-VN")}
          </option>
        ))}
    </select>
  );

  const ReportPanel = ({ report }: { report: Report | null }) => {
    if (!report) {
      return (
        <div className="card text-center text-gray-400 py-12">
          Chon bao cao de so sanh
        </div>
      );
    }
    return (
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${MODULE_COLORS[report.module]}`}>
            {report.module}
          </span>
          <span className="text-sm font-medium text-gray-900 flex-1">{report.input_query}</span>
          <span className="text-xs text-gray-400">
            {new Date(report.created_at).toLocaleDateString("vi-VN")}
          </span>
        </div>
        {report.summary && (
          <p className="text-sm text-gray-600 mb-4 pb-4 border-b border-gray-100">{report.summary}</p>
        )}
        <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-table:text-sm overflow-auto max-h-[600px]">
          <ReactMarkdown>{report.raw_markdown || ""}</ReactMarkdown>
        </div>
      </div>
    );
  };

  return (
    <>
      <Header title="So sanh bao cao" description="So sanh 2 bao cao canh nhau de thay su khac biet" />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Bao cao 1</label>
          <ReportSelector value={leftId} onChange={setLeftId} excludeId={rightId} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Bao cao 2</label>
          <ReportSelector value={rightId} onChange={setRightId} excludeId={leftId} />
        </div>
      </div>

      {leftReport && rightReport && leftReport.module === rightReport.module && (
        <ComparisonSummary left={leftReport} right={rightReport} />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ReportPanel report={leftReport} />
        <ReportPanel report={rightReport} />
      </div>
    </>
  );
}

function ComparisonSummary({ left, right }: { left: Report; right: Report }) {
  const leftDate = new Date(left.created_at);
  const rightDate = new Date(right.created_at);
  const newer = leftDate > rightDate ? "Bao cao 1" : "Bao cao 2";

  return (
    <div className="card bg-blue-50 border-blue-200 mb-6">
      <div className="flex items-center gap-2 mb-2">
        <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
        <h3 className="font-semibold text-blue-900">So sanh</h3>
      </div>
      <div className="text-sm text-blue-800 space-y-1">
        <p>Module: <span className="font-medium">{left.module}</span></p>
        <p>Query 1: <span className="font-medium">{left.input_query}</span></p>
        <p>Query 2: <span className="font-medium">{right.input_query}</span></p>
        <p>{newer} moi hon ({Math.abs(Math.round((leftDate.getTime() - rightDate.getTime()) / (1000 * 60 * 60 * 24)))} ngay)</p>
      </div>
    </div>
  );
}
