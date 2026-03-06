"use client";

import { SEVERITY_COLORS } from "@/lib/constants";
import type { AuditIssueData } from "@/lib/types";

export default function IssueList({ issues }: { issues: AuditIssueData[] }) {
  if (!issues.length) return null;

  const grouped: Record<string, AuditIssueData[]> = {};
  for (const issue of issues) {
    if (!grouped[issue.severity]) grouped[issue.severity] = [];
    grouped[issue.severity].push(issue);
  }

  const order = ["Critical", "Warning", "Info"];

  return (
    <div className="space-y-4">
      {order.map((severity) => {
        const items = grouped[severity];
        if (!items?.length) return null;
        return (
          <div key={severity}>
            <h3 className={`inline-block text-sm font-medium px-3 py-1 rounded-full mb-3 ${SEVERITY_COLORS[severity]}`}>
              {severity} ({items.length})
            </h3>
            <div className="space-y-2">
              {items.map((issue) => (
                <div key={issue.id} className={`border rounded-lg p-4 ${SEVERITY_COLORS[issue.severity]}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100">{issue.title}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{issue.category}</p>
                    </div>
                    {issue.effort_level && (
                      <span className="text-xs bg-white/80 px-2 py-0.5 rounded-full">{issue.effort_level}</span>
                    )}
                  </div>
                  {issue.description && <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">{issue.description}</p>}
                  {issue.fix_suggestion && (
                    <div className="mt-2 bg-white/50 dark:bg-gray-800/50 rounded p-2">
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Cach sua:</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{issue.fix_suggestion}</p>
                    </div>
                  )}
                  {issue.code_snippet && (
                    <pre className="mt-2 bg-gray-900 text-green-400 text-xs p-3 rounded overflow-x-auto">
                      {issue.code_snippet}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
