import { apiFetch } from "@/lib/api/client";

export type ProjectListItem = {
  id: number;
  name: string;
  source_type: string;
  status: string;
  description: string | null;
  created_at: string | null;
  updated_at: string | null;
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

export function fetchProjects(
  token: string,
): Promise<PagedResponse<ProjectListItem>> {
  return apiFetch<PagedResponse<ProjectListItem>>("/projects", {
    headers: authHeaders(token),
  });
}

export function fetchProject(
  token: string,
  projectId: number,
): Promise<ProjectListItem> {
  return apiFetch<ProjectListItem>(`/projects/${projectId}`, {
    headers: authHeaders(token),
  });
}

export function createProject(
  token: string,
  input: { name: string; source_type: string; description?: string },
): Promise<ProjectListItem> {
  return apiFetch<ProjectListItem>("/projects", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(input),
  });
}

export function updateProject(
  token: string,
  projectId: number,
  input: { name?: string; description?: string },
): Promise<ProjectListItem> {
  return apiFetch<ProjectListItem>(`/projects/${projectId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(input),
  });
}

export function archiveProject(
  token: string,
  projectId: number,
): Promise<ProjectListItem> {
  return apiFetch<ProjectListItem>(`/projects/${projectId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}
