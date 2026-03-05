"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import { vi } from "@/i18n/vi";
import { useRouter } from "next/navigation";
import { getReports, deleteReport, retryReport } from "@/lib/api";
import { MODULE_COLORS, STATUS_COLORS } from "@/lib/constants";
import type { ReportListItem } from "@/lib/types";

export default function ReportsPage() {
  const router = useRouter();
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    loadReports();
  }, [filter]);

  const loadReports = async () => {
    const params: Record<string, string> = { limit: "100" };
    if (filter) params.module = filter;
    const data = await getReports(params).catch(() => []);
    setReports(data);
  };

  const handleDelete = async (id: string) => {
    if (!confirm(vi.reports.confirmDelete)) return;
    await deleteReport(id);
    loadReports();
  };

  const modules = ["", "keywords", "competitor", "content", "audit", "full", "strategy", "fix"];

  return (
    <>
      <Header title={vi.reports.title} description={vi.reports.description} />

      <div className="flex flex-wrap gap-2 mb-6">
        {modules.map((m) => (
          <button
            key={m}
            onClick={() => setFilter(m)}
            className={`text-sm px-3 py-1.5 rounded-full ${
              filter === m ? "bg-primary-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {m || "Tat ca"}
          </button>
        ))}
      </div>

      {reports.length > 0 ? (
        <div className="card">
          <div className="space-y-2">
            {reports.map((r) => (
              <div key={r.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-3 px-4 rounded-lg hover:bg-gray-50 border-b border-gray-100 last:border-0 gap-2">
                <Link href={`/reports/${r.id}`} className="flex-1 flex items-center gap-4">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${MODULE_COLORS[r.module]}`}>
                    {r.module}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{r.input_query}</p>
                    {r.summary && <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{r.summary}</p>}
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${STATUS_COLORS[r.status]}`}>
                    {vi.common.status[r.status as keyof typeof vi.common.status]}
                  </span>
                  <span className="text-xs text-gray-400 w-24 text-right">
                    {new Date(r.created_at).toLocaleDateString("vi-VN")}
                  </span>
                </Link>
                <div className="flex items-center gap-2 ml-4">
                  {r.status === "failed" && (
                    <button
                      onClick={async () => {
                        const res = await retryReport(r.id);
                        router.push(`/${r.module === "full" || r.module === "strategy" || r.module === "fix" ? r.module : r.module}`);
                      }}
                      className="text-xs text-primary-600 hover:text-primary-800 font-medium"
                      title={vi.common.retry}
                    >
                      {vi.common.retry}
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(r.id)}
                    className="text-gray-400 hover:text-red-500 text-sm"
                    title={vi.reports.delete}
                  >
                    &#10005;
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="card text-center text-gray-500 py-12">
          {vi.reports.empty}
        </div>
      )}
    </>
  );
}
