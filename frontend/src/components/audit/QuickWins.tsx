"use client";

import { vi } from "@/i18n/vi";

interface QuickWin {
  title: string;
  description: string;
  effort_level: string;
}

export default function QuickWins({ wins }: { wins: QuickWin[] | any | null }) {
  const items: QuickWin[] = Array.isArray(wins) ? wins :
    (wins && typeof wins === "object" && Array.isArray(wins.items)) ? wins.items : [];
  if (!items.length) return null;

  return (
    <div className="card border-2 border-green-200 dark:border-green-700 bg-green-50/30 dark:bg-green-900/20">
      <h3 className="font-semibold text-green-800 dark:text-green-200 mb-4">{vi.audit.quickWins}</h3>
      <div className="space-y-3">
        {items.map((win, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-green-200 dark:border-green-700">
            <div className="flex items-start justify-between">
              <p className="font-medium text-gray-900 dark:text-gray-100">{i + 1}. {win.title}</p>
              <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-0.5 rounded-full">{win.effort_level}</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{win.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
