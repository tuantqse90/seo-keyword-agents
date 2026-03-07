"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line, AreaChart, Area,
} from "recharts";
import Header from "@/components/layout/Header";
import {
  getAnalyticsOverview, getPopularModules, getDailyTrend,
  getTopQueries, getModuleSuccessRates,
} from "@/lib/api";

const MODULE_COLORS: Record<string, string> = {
  keywords: "#3b82f6",
  competitor: "#8b5cf6",
  content: "#22c55e",
  audit: "#f97316",
  full: "#6366f1",
  strategy: "#14b8a6",
  fix: "#ef4444",
};

const MODULE_LABELS: Record<string, string> = {
  keywords: "Tu khoa",
  competitor: "Doi thu",
  content: "Noi dung",
  audit: "Kiem tra",
  full: "Day du",
  strategy: "Chien luoc",
  fix: "Sua nhanh",
};

const PERIOD_OPTIONS = [
  { value: 7, label: "7 ngay" },
  { value: 30, label: "30 ngay" },
  { value: 90, label: "90 ngay" },
  { value: 365, label: "1 nam" },
];

export default function AnalyticsPage() {
  const [days, setDays] = useState(30);
  const [overview, setOverview] = useState<any>(null);
  const [modules, setModules] = useState<any[]>([]);
  const [daily, setDaily] = useState<any[]>([]);
  const [topQueries, setTopQueries] = useState<any[]>([]);
  const [successRates, setSuccessRates] = useState<any[]>([]);

  useEffect(() => {
    getAnalyticsOverview(days).then(setOverview).catch(() => {});
    getPopularModules(days).then((d) => setModules(d.modules || [])).catch(() => {});
    getDailyTrend(days).then((d) => setDaily(d.daily || [])).catch(() => {});
    getTopQueries(days).then((d) => setTopQueries(d.queries || [])).catch(() => {});
    getModuleSuccessRates(days).then((d) => setSuccessRates(d.modules || [])).catch(() => {});
  }, [days]);

  const pieData = modules.map((m) => ({
    name: MODULE_LABELS[m.module] || m.module,
    value: m.count,
    color: MODULE_COLORS[m.module] || "#6b7280",
  }));

  return (
    <>
      <Header title="Phan tich & Thong ke" />

      {/* Period selector */}
      <div className="flex gap-2 mb-6">
        {PERIOD_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setDays(opt.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              days === opt.value
                ? "bg-blue-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Overview cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-gray-400">Tong bao cao</p>
          <p className="text-3xl font-bold text-blue-600 mt-1">{overview?.total_reports || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-gray-400">Ti le thanh cong</p>
          <p className="text-3xl font-bold text-green-600 mt-1">{overview?.success_rate || 0}%</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-gray-400">TB moi ngay</p>
          <p className="text-3xl font-bold text-purple-600 mt-1">{overview?.avg_per_day || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-gray-400">That bai</p>
          <p className="text-3xl font-bold text-red-600 mt-1">{overview?.by_status?.failed || 0}</p>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Daily trend */}
        {daily.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">Xu huong hang ngay</h3>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={daily}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="completed" stackId="1" stroke="#22c55e" fill="#22c55e" fillOpacity={0.3} name="Thanh cong" />
                <Area type="monotone" dataKey="failed" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} name="That bai" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Module distribution */}
        {pieData.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">Module pho bien</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Success rates per module */}
      {successRates.length > 0 && (
        <div className="card mb-8">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">Ti le thanh cong theo module</h3>
          <div className="space-y-3">
            {successRates.map((m) => (
              <div key={m.module} className="flex items-center gap-4">
                <span className="text-sm font-medium w-24 text-gray-700 dark:text-gray-300">
                  {MODULE_LABELS[m.module] || m.module}
                </span>
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${m.success_rate}%`,
                      backgroundColor: MODULE_COLORS[m.module] || "#6b7280",
                    }}
                  />
                </div>
                <span className="text-sm font-mono w-16 text-right text-gray-600 dark:text-gray-400">
                  {m.success_rate}%
                </span>
                <span className="text-xs text-gray-400 w-20 text-right">
                  {m.completed}/{m.total}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top queries */}
      {topQueries.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">Query duoc phan tich nhieu nhat</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b dark:border-gray-700">
                  <th className="text-left py-2 px-3 text-gray-500 dark:text-gray-400">#</th>
                  <th className="text-left py-2 px-3 text-gray-500 dark:text-gray-400">Query / URL</th>
                  <th className="text-right py-2 px-3 text-gray-500 dark:text-gray-400">So lan</th>
                </tr>
              </thead>
              <tbody>
                {topQueries.map((q, i) => (
                  <tr key={i} className="border-b dark:border-gray-700 last:border-0">
                    <td className="py-2 px-3 text-gray-400">{i + 1}</td>
                    <td className="py-2 px-3 text-gray-700 dark:text-gray-300 truncate max-w-md">{q.query}</td>
                    <td className="py-2 px-3 text-right font-mono text-gray-600 dark:text-gray-400">{q.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}
