"use client";

export default function Header({ title, description }: { title: string; description?: string }) {
  return (
    <div className="mb-8">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{title}</h1>
      {description && <p className="text-gray-500 dark:text-gray-400 mt-1">{description}</p>}
    </div>
  );
}
