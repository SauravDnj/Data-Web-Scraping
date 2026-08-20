import { apiFetch } from "@/lib/api/client";

export type JobSummary = {
  active_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
};

export type JobCounters = {
  total_units: number;
  successful_units: number;
  failed_units: number;
  skipped_units: number;
  records_created: number;
  records_updated: number;
  records_rejected: number;
};

export type JobListItem = {
  id: number;
  project_id: number;
  status: string;
  counters: JobCounters;
  requested_at: string | null;
  started_at: string | null;
  finished_at: string | null;
  error_code: string | null;
  error_message: string | null;
};

export type PagedResponse<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
};

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export function fetchJobSummary(token: string): Promise<JobSummary> {
  return apiFetch<JobSummary>("/jobs/summary", { headers: authHeaders(token) });
}

export function fetchJobs(
  token: string,
  params: { status?: string; limit?: number } = {},
): Promise<PagedResponse<JobListItem>> {
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);
  if (params.limit) query.set("limit", String(params.limit));
  const qs = query.toString();
  return apiFetch<PagedResponse<JobListItem>>(`/jobs${qs ? `?${qs}` : ""}`, {
    headers: authHeaders(token),
  });
}

export function fetchRecordCount(token: string): Promise<{ total: number }> {
  return apiFetch<{ total: number }>("/records/count", {
    headers: authHeaders(token),
  });
}
