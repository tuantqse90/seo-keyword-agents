"use client";

export default function TechChecklist({ checklist }: { checklist: Record<string, boolean> | null }) {
  if (!checklist) return null;

  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">Kiem tra ky thuat</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {Object.entries(checklist).map(([check, passed]) => (
          <div key={check} className="flex items-center gap-2 text-sm">
            <span className={passed ? "text-green-500" : "text-red-500"}>
              {passed ? "\u2713" : "\u2717"}
            </span>
            <span className="text-gray-700 dark:text-gray-300">{check}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
