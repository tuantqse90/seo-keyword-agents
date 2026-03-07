"use client";

import { getExportUrl } from "@/lib/api";
import { useLanguage } from "@/hooks/useLanguage";

interface ExportButtonProps {
  reportId: string;
}

export default function ExportButton({ reportId }: ExportButtonProps) {
  const { t: vi } = useLanguage();
  return (
    <div className="flex gap-2">
      <a
        href={getExportUrl(reportId, "csv")}
        download
        className="btn-secondary text-sm"
      >
        {vi.reports.exportCsv}
      </a>
      <a
        href={getExportUrl(reportId, "pdf")}
        download
        className="btn-secondary text-sm"
      >
        {vi.reports.exportPdf}
      </a>
    </div>
  );
}
