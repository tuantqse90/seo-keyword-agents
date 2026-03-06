const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...getAuthHeaders(), ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `API error: ${res.status}`);
  }
  return res.json();
}

// Projects
export const getProjects = () => fetchApi<any[]>("/api/projects");
export const createProject = (data: { name: string; url?: string; description?: string }) =>
  fetchApi<any>("/api/projects", { method: "POST", body: JSON.stringify(data) });
export const deleteProject = (id: string) =>
  fetch(`${API_BASE}/api/projects/${id}`, { method: "DELETE" });

// Analysis
export const startAnalysis = (module: string, query: string, projectId?: string) =>
  fetchApi<{ report_id: string; stream_url: string }>(`/api/${module}/analyze`, {
    method: "POST",
    body: JSON.stringify({ query, project_id: projectId }),
  });

// Workflows
export const startWorkflow = (type: string, query: string, projectId?: string) =>
  fetchApi<{ report_id: string; stream_url: string }>(`/api/workflows/${type}`, {
    method: "POST",
    body: JSON.stringify({ query, project_id: projectId }),
  });

// Reports
export const getReports = (params?: Record<string, string>) => {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetchApi<any[]>(`/api/reports${qs}`);
};

export const getReport = (id: string) => fetchApi<any>(`/api/reports/${id}`);
export const searchReports = (q: string) =>
  fetchApi<any[]>(`/api/reports/search?q=${encodeURIComponent(q)}&limit=20`);

export const getReportStats = () => fetchApi<{
  total: number;
  by_module: Record<string, number>;
  by_status: Record<string, number>;
  daily: Array<{ date: string; count: number }>;
}>("/api/reports/stats");
export const deleteReport = (id: string) =>
  fetch(`${API_BASE}/api/reports/${id}`, { method: "DELETE" });

export const retryReport = (id: string) =>
  fetchApi<{ report_id: string; stream_url: string }>(`/api/reports/${id}/retry`, { method: "POST" });

// Module-specific results
export const getKeywordReport = (id: string) => fetchApi<any>(`/api/keywords/${id}`);
export const getCompetitorReport = (id: string) => fetchApi<any>(`/api/competitor/${id}`);
export const getContentReport = (id: string) => fetchApi<any>(`/api/content/${id}`);
export const getAuditReport = (id: string) => fetchApi<any>(`/api/audit/${id}`);

// Auth
export const loginApi = (email: string, password: string) =>
  fetchApi<{ token: string; user: { id: string; email: string; name: string } }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const registerApi = (email: string, password: string, name: string) =>
  fetchApi<{ token: string; user: { id: string; email: string; name: string } }>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, name }),
  });

export const getMe = () => fetchApi<{ id: string; email: string; name: string }>("/api/auth/me");

// Schedules
export const getSchedules = () => fetchApi<any[]>("/api/schedules");
export const createSchedule = (data: { module: string; query: string; interval_hours: number; project_id?: string }) =>
  fetchApi<any>("/api/schedules", { method: "POST", body: JSON.stringify(data) });
export const updateSchedule = (id: string, data: { interval_hours?: number; is_active?: boolean; query?: string }) =>
  fetchApi<any>(`/api/schedules/${id}`, { method: "PUT", body: JSON.stringify(data) });
export const deleteSchedule = (id: string) =>
  fetch(`${API_BASE}/api/schedules/${id}`, { method: "DELETE" });

// Export
export const getExportUrl = (reportId: string, format: "csv" | "pdf") =>
  `${API_BASE}/api/reports/${reportId}/export/${format}`;
