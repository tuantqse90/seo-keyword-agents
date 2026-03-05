"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import { vi } from "@/i18n/vi";
import { getReports } from "@/lib/api";
import { MODULE_COLORS, STATUS_COLORS } from "@/lib/constants";
import type { ReportListItem } from "@/lib/types";

const quickActions = [
  { href: "/keywords", label: vi.nav.keywords, desc: vi.keywords.description, color: "border-blue-200 hover:border-blue-400" },
  { href: "/competitor", label: vi.nav.competitor, desc: vi.competitor.description, color: "border-purple-200 hover:border-purple-400" },
  { href: "/content", label: vi.nav.content, desc: vi.content.description, color: "border-green-200 hover:border-green-400" },
  { href: "/audit", label: vi.nav.audit, desc: vi.audit.description, color: "border-orange-200 hover:border-orange-400" },
  { href: "/full", label: vi.workflows.full.title, desc: vi.workflows.full.description, color: "border-indigo-200 hover:border-indigo-400" },
  { href: "/strategy", label: vi.workflows.strategy.title, desc: vi.workflows.strategy.description, color: "border-teal-200 hover:border-teal-400" },
];

export default function DashboardPage() {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [totalReports, setTotalReports] = useState(0);

  useEffect(() => {
    getReports({ limit: "5" }).then((data) => {
      setReports(data);
      setTotalReports(data.length);
    }).catch(() => {});
  }, []);

  return (
    <>
      <Header title={vi.dashboard.welcome} />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500">{vi.dashboard.totalReports}</p>
          <p className="text-3xl font-bold text-primary-700 mt-1">{totalReports}</p>
        </div>
      </div>

      <h2 className="text-lg font-semibold mb-4">{vi.dashboard.quickActions}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {quickActions.map((action) => (
          <Link key={action.href} href={action.href}>
            <div className={`card border-2 ${action.color} transition-colors cursor-pointer`}>
              <h3 className="font-semibold text-gray-900">{action.label}</h3>
              <p className="text-sm text-gray-500 mt-1">{action.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      <h2 className="text-lg font-semibold mb-4">{vi.dashboard.recentActivity}</h2>
      {reports.length > 0 ? (
        <div className="card">
          <div className="space-y-3">
            {reports.map((r) => (
              <Link key={r.id} href={`/reports/${r.id}`}>
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 cursor-pointer gap-2">
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${MODULE_COLORS[r.module]}`}>
                      {r.module}
                    </span>
                    <span className="text-sm text-gray-700">{r.input_query}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${STATUS_COLORS[r.status]}`}>
                      {vi.common.status[r.status as keyof typeof vi.common.status]}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(r.created_at).toLocaleDateString("vi-VN")}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ) : (
        <div className="card text-center text-gray-500 py-8">
          {vi.reports.empty}
        </div>
      )}
    </>
  );
}
