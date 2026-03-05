"use client";

import clsx from "clsx";

interface ScoreBadgeProps {
  score: number;
  max?: number;
  label?: string;
  size?: "sm" | "lg";
}

export default function ScoreBadge({ score, max = 100, label, size = "sm" }: ScoreBadgeProps) {
  const pct = (score / max) * 100;
  const color = pct >= 80 ? "text-green-600" : pct >= 60 ? "text-yellow-600" : pct >= 40 ? "text-orange-600" : "text-red-600";
  const bg = pct >= 80 ? "bg-green-100" : pct >= 60 ? "bg-yellow-100" : pct >= 40 ? "bg-orange-100" : "bg-red-100";

  return (
    <div className={clsx("inline-flex items-center gap-2 rounded-lg px-3 py-1", bg)}>
      <span className={clsx("font-bold", color, size === "lg" ? "text-2xl" : "text-sm")}>
        {score}/{max}
      </span>
      {label && <span className="text-xs text-gray-600">{label}</span>}
    </div>
  );
}
