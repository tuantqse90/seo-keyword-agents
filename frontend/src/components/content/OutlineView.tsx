"use client";

interface OutlineItem {
  heading: string;
  level: number;
  key_points: string[];
}

export default function OutlineView({ outline }: { outline: OutlineItem[] | any | null }) {
  const items: OutlineItem[] = Array.isArray(outline) ? outline :
    (outline && typeof outline === "object" && Array.isArray(outline.sections)) ? outline.sections : [];
  if (!items.length) return null;

  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">Dan y noi dung</h3>
      <div className="space-y-3">
        {items.map((item, i) => (
          <div key={i} className={item.level === 3 ? "ml-6" : ""}>
            <p className={`font-medium ${item.level === 2 ? "text-gray-900 dark:text-gray-100 text-base" : "text-gray-700 dark:text-gray-300 text-sm"}`}>
              {item.level === 2 ? "H2: " : "H3: "}
              {item.heading}
            </p>
            {item.key_points?.length > 0 && (
              <ul className="mt-1 ml-4 space-y-0.5">
                {item.key_points.map((point, j) => (
                  <li key={j} className="text-xs text-gray-500 dark:text-gray-400">- {point}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
