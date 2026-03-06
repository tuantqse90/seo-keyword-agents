"use client";

export default function LsiKeywords({ keywords }: { keywords: string[] | any | null }) {
  const items: string[] = Array.isArray(keywords) ? keywords :
    (keywords && typeof keywords === "object" && Array.isArray(keywords.items)) ? keywords.items : [];
  if (!items.length) return null;

  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">Tu khoa LSI / Ngu nghia</h3>
      <div className="flex flex-wrap gap-2">
        {items.map((kw, i) => (
          <span key={i} className="text-sm bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300 px-3 py-1 rounded-full">
            {kw}
          </span>
        ))}
      </div>
    </div>
  );
}
