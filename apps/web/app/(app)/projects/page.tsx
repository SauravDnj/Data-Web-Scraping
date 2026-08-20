"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth/AuthContext";
import { fetchProjects, type ProjectListItem } from "@/lib/api/projects";
import { EmptyState } from "@/components/feedback/EmptyState";
import { ErrorState } from "@/components/feedback/ErrorState";
import { Button } from "@/components/ui/Button";
import { ProjectStatusBadge } from "@/components/projects/ProjectStatusBadge";

type LoadState = "loading" | "error" | "ready";

export default function ProjectsPage() {
  const { token } = useAuth();
  const [state, setState] = useState<LoadState>("loading");
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  // Same react-hooks/set-state-in-effect-safe shape as the dashboard
  // (docs/16_MEMORY.md, T071): inline .then()/.catch() in the effect,
  // a bumped token to re-trigger it for retry.
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    fetchProjects(token)
      .then((page) => {
        if (cancelled) return;
        setProjects(page.items);
        setState("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, [token, reloadToken]);

  function retry() {
    setState("loading");
    setReloadToken((count) => count + 1);
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Projects
        </h1>
        <Link href="/projects/new">
          <Button>New Project</Button>
        </Link>
      </div>

      {state === "loading" ? (
        <div
          className="flex items-center justify-center py-16"
          role="status"
          aria-label="Loading projects"
        >
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900 dark:border-zinc-700 dark:border-t-zinc-50" />
        </div>
      ) : state === "error" ? (
        <ErrorState message="Could not load projects." retryable onRetry={retry} />
      ) : projects.length === 0 ? (
        <EmptyState
          title="No projects yet"
          description="Create a project to configure a Google Maps data collection source."
          action={
            <Link href="/projects/new">
              <Button>New Project</Button>
            </Link>
          }
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-zinc-200 text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {projects.map((project) => (
                <tr key={project.id}>
                  <td className="px-4 py-2">
                    <Link
                      href={`/projects/${project.id}`}
                      className="font-medium text-zinc-900 hover:underline dark:text-zinc-50"
                    >
                      {project.name}
                    </Link>
                  </td>
                  <td className="px-4 py-2">
                    <ProjectStatusBadge status={project.status} />
                  </td>
                  <td className="px-4 py-2 text-zinc-600 dark:text-zinc-400">
                    {project.source_type}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
