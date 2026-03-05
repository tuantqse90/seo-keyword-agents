"use client";

import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import { MODULE_COLORS } from "@/lib/constants";
import { getSchedules, createSchedule, updateSchedule, deleteSchedule } from "@/lib/api";

interface ScheduleItem {
  id: string;
  module: string;
  query: string;
  interval_hours: number;
  is_active: boolean;
  last_run_at: string | null;
  next_run_at: string;
  created_at: string;
}

const INTERVAL_OPTIONS = [
  { label: "6 gio", value: 6 },
  { label: "12 gio", value: 12 },
  { label: "Hang ngay", value: 24 },
  { label: "3 ngay", value: 72 },
  { label: "Hang tuan", value: 168 },
  { label: "2 tuan", value: 336 },
  { label: "Hang thang", value: 720 },
];

const MODULES = ["keywords", "competitor", "content", "audit", "full", "strategy", "fix"];

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<ScheduleItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formModule, setFormModule] = useState("audit");
  const [formQuery, setFormQuery] = useState("");
  const [formInterval, setFormInterval] = useState(168);

  const loadSchedules = () => {
    getSchedules().then(setSchedules).catch(() => []);
  };

  useEffect(() => { loadSchedules(); }, []);

  const handleCreate = async () => {
    if (!formQuery.trim()) return;
    await createSchedule({ module: formModule, query: formQuery, interval_hours: formInterval });
    setFormQuery("");
    setShowForm(false);
    loadSchedules();
  };

  const handleToggle = async (s: ScheduleItem) => {
    await updateSchedule(s.id, { is_active: !s.is_active });
    loadSchedules();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Ban co chac muon xoa lich hen nay?")) return;
    await deleteSchedule(id);
    loadSchedules();
  };

  return (
    <>
      <Header title="Lich phan tich tu dong" description="Len lich chay phan tich dinh ky" />

      <div className="flex justify-end mb-4">
        <button onClick={() => setShowForm(!showForm)} className="btn-primary text-sm">
          + Tao lich moi
        </button>
      </div>

      {showForm && (
        <div className="card mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Tao lich phan tich moi</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Module</label>
              <select
                value={formModule}
                onChange={(e) => setFormModule(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                {MODULES.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tan suat</label>
              <select
                value={formInterval}
                onChange={(e) => setFormInterval(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                {INTERVAL_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">URL / Tu khoa</label>
              <input
                value={formQuery}
                onChange={(e) => setFormQuery(e.target.value)}
                placeholder="VD: example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <button onClick={() => setShowForm(false)} className="btn-secondary text-sm">Huy</button>
            <button onClick={handleCreate} className="btn-primary text-sm">Tao lich</button>
          </div>
        </div>
      )}

      {schedules.length > 0 ? (
        <div className="card">
          <div className="space-y-2">
            {schedules.map((s) => (
              <div key={s.id} className={`flex items-center justify-between py-3 px-4 rounded-lg border-b border-gray-100 last:border-0 ${s.is_active ? "" : "opacity-50"}`}>
                <div className="flex items-center gap-4 flex-1">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${MODULE_COLORS[s.module]}`}>
                    {s.module}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{s.query}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {INTERVAL_OPTIONS.find((o) => o.value === s.interval_hours)?.label || `${s.interval_hours}h`}
                      {s.last_run_at && ` — Lan cuoi: ${new Date(s.last_run_at).toLocaleString("vi-VN")}`}
                    </p>
                  </div>
                  <div className="text-xs text-gray-400">
                    Lan toi: {new Date(s.next_run_at).toLocaleString("vi-VN")}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => handleToggle(s)}
                    className={`text-xs px-2 py-1 rounded-full font-medium ${s.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}
                  >
                    {s.is_active ? "Dang bat" : "Da tat"}
                  </button>
                  <button
                    onClick={() => handleDelete(s.id)}
                    className="text-gray-400 hover:text-red-500 text-sm"
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
          Chua co lich phan tich nao
        </div>
      )}
    </>
  );
}
