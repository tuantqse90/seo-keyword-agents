"use client";

import type { ContentBriefData } from "@/lib/types";

export default function MetaPreview({ brief }: { brief: ContentBriefData }) {
  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 mb-4">Xem truoc Meta</h3>

      {/* Google SERP preview */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <p className="text-xs text-gray-400 mb-1">google.com</p>
        <p className="text-lg text-blue-700 hover:underline cursor-pointer">
          {brief.title_tag || "Title tag chua co"}
        </p>
        <p className="text-sm text-gray-600 mt-1">
          {brief.meta_description || "Meta description chua co"}
        </p>
        <div className="flex gap-4 mt-2 text-xs text-gray-400">
          {brief.title_tag && <span>Title: {brief.title_tag.length}/60 ky tu</span>}
          {brief.meta_description && <span>Meta: {brief.meta_description.length}/155 ky tu</span>}
        </div>
      </div>

      {brief.target_word_count && (
        <p className="text-sm text-gray-600">
          So luong tu muc tieu: <span className="font-bold">{brief.target_word_count.toLocaleString()}</span> tu
        </p>
      )}

      {brief.snippet_strategy && (
        <div className="mt-3">
          <p className="text-xs font-medium text-gray-500 mb-1">Chien luoc Featured Snippet</p>
          <p className="text-sm text-gray-700">{brief.snippet_strategy}</p>
        </div>
      )}
    </div>
  );
}
