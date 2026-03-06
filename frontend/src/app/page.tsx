"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import Header from "@/components/layout/Header";
import { vi } from "@/i18n/vi";
import { getReports, getReportStats } from "@/lib/api";
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

const PIE_COLORS = ["#3b82f6", "#8b5cf6", "#22c55e", "#f97316", "#6366f1", "#14b8a6", "#ef4444"];
const MODULE_LABELS: Record<string, string> = {
  keywords: "Tu khoa",
  competitor: "Doi thu",
  content: "Noi dung",
  audit: "Kiem tra",
  full: "Day du",
  strategy: "Chien luoc",
  fix: "Sua nhanh",
};

interface Stats {
  total: number;
  by_module: Record<string, number>;
  by_status: Record<string, number>;
  daily: Array<{ date: string; count: number }>;
}

export default function DashboardPage() {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    getReports({ limit: "5" }).then(setReports).catch(() => {});
    getReportStats().then(setStats).catch(() => {});
  }, []);

  const moduleData = stats
    ? Object.entries(stats.by_module).map(([key, value]) => ({
        name: MODULE_LABELS[key] || key,
        value,
      }))
    : [];

  const statusData = stats
    ? Object.entries(stats.by_status).map(([key, value]) => ({
        name: vi.common.status[key as keyof typeof vi.common.status] || key,
        value,
      }))
    : [];

  return (
    <>
      <Header title={vi.dashboard.welcome} />

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-gray-400">{vi.dashboard.totalReports}</p>
          <p className="text-3xl font-bold text-primary-700 dark:text-primary-400 mt-1">{stats?.total || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-gray-400">Hoan thanh</p>
          <p className="text-3xl font-bold text-green-600 mt-1">{stats?.by_status?.completed || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-gray-400">Dang xu ly</p>
          <p className="text-3xl font-bold text-yellow-600 mt-1">{(stats?.by_status?.streaming || 0) + (stats?.by_status?.pending || 0)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-gray-400">That bai</p>
          <p className="text-3xl font-bold text-red-600 mt-1">{stats?.by_status?.failed || 0}</p>
        </div>
      </div>

      {/* Charts */}
      {stats && (stats.daily.length > 0 || moduleData.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Daily trend */}
          {stats.daily.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">Bao cao theo ngay</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={stats.daily}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} tickFormatter={(v) => v.slice(5)} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Bao cao" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Module distribution */}
          {moduleData.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">Phan bo theo module</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={moduleData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {moduleData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Quick actions */}
      <h2 className="text-lg font-semibold mb-4 dark:text-gray-100">{vi.dashboard.quickActions}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {quickActions.map((action) => (
          <Link key={action.href} href={action.href}>
            <div className={`card border-2 ${action.color} transition-colors cursor-pointer`}>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">{action.label}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{action.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Recent activity */}
      <h2 className="text-lg font-semibold mb-4 dark:text-gray-100">{vi.dashboard.recentActivity}</h2>
      {reports.length > 0 ? (
        <div className="card">
          <div className="space-y-3">
            {reports.map((r) => (
              <Link key={r.id} href={`/reports/${r.id}`}>
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer gap-2">
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${MODULE_COLORS[r.module]}`}>
                      {r.module}
                    </span>
                    <span className="text-sm text-gray-700 dark:text-gray-300">{r.input_query}</span>
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
