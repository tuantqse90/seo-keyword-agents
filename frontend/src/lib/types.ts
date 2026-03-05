export type ReportStatus = "pending" | "streaming" | "completed" | "failed";
export type ReportModule = "keywords" | "competitor" | "content" | "audit" | "full" | "strategy" | "fix";
export type Severity = "Critical" | "Warning" | "Info";
export type EffortLevel = "[Quick Win]" | "[Medium Effort]" | "[Strategic Investment]";

export interface Project {
  id: string;
  name: string;
  url: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Report {
  id: string;
  project_id: string | null;
  module: ReportModule;
  input_query: string;
  status: ReportStatus;
  raw_markdown: string | null;
  summary: string | null;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ReportListItem {
  id: string;
  project_id: string | null;
  module: ReportModule;
  input_query: string;
  status: ReportStatus;
  summary: string | null;
  created_at: string;
}

export interface KeywordData {
  id: string;
  keyword: string;
  cluster: string | null;
  search_volume: number | null;
  keyword_difficulty: number | null;
  search_intent: string | null;
  cpc: number | null;
  opportunity_score: number | null;
  is_golden: boolean;
}

export interface CompetitorData {
  id: string;
  name: string;
  url: string | null;
  estimated_traffic: number | null;
  domain_authority: number | null;
  top_keywords: Record<string, unknown> | null;
  strengths: Record<string, unknown> | null;
  weaknesses: Record<string, unknown> | null;
}

export interface KeywordGapData {
  id: string;
  keyword: string;
  target_rank: number | null;
  competitor_ranks: Record<string, number> | null;
}

export interface ContentBriefData {
  id: string;
  title_tag: string | null;
  meta_description: string | null;
  target_word_count: number | null;
  outline: Array<{ heading: string; level: number; key_points: string[] }> | null;
  lsi_keywords: string[] | null;
  snippet_strategy: string | null;
  eeat_signals: string[] | null;
}

export interface AuditIssueData {
  id: string;
  severity: Severity;
  category: string;
  title: string;
  description: string | null;
  fix_suggestion: string | null;
  code_snippet: string | null;
  effort_level: string | null;
}

export interface AuditResultData {
  id: string;
  overall_score: number | null;
  letter_grade: string | null;
  quick_wins: Array<{ title: string; description: string; effort_level: string }> | null;
  tech_checklist: Record<string, boolean> | null;
  issues: AuditIssueData[];
}

export interface AnalyzeResponse {
  report_id: string;
  stream_url: string;
}
