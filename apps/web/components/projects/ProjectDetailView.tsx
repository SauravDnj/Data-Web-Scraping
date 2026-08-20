"use client";

import { useEffect, useState } from "react";
import {
  archiveProject,
  fetchProject,
  updateProject,
  type ProjectListItem,
} from "@/lib/api/projects";
import { useAuth } from "@/lib/auth/AuthContext";
import { useToast } from "@/components/feedback/Toast";
import { ErrorState } from "@/components/feedback/ErrorState";
import { ProjectStatusBadge } from "@/components/projects/ProjectStatusBadge";
import { ProjectForm } from "@/components/projects/ProjectForm";
import { Button } from "@/components/ui/Button";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";

type LoadState = "loading" | "error" | "ready";

/** All of the project detail page's actual logic, taking a plain
 * `projectId` rather than the Next.js `Promise<params>` its page
 * wrapper (`app/(app)/projects/[projectId]/page.tsx`) unwraps via
 * `use()`. Split out so this is unit-testable without a Suspense
 * boundary — `use()` on a plain `Promise.resolve()` does not reliably
 * settle under this project's test stack (vitest + jsdom + React 19),
 * confirmed with a minimal isolated repro; the real Next.js runtime
 * (verified via `next build` and a real dev server) has no such
 * issue, since it provides its own Suspense machinery around every
 * page. */
export function ProjectDetailView({ projectId }: { projectId: number }) {
  const { token } = useAuth();
  const { push } = useToast();

  const [state, setState] = useState<LoadState>("loading");
  const [project, setProject] = useState<ProjectListItem | null>(null);
  const [editing, setEditing] = useState(false);
  const [confirmingArchive, setConfirmingArchive] = useState(false);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    fetchProject(token, projectId)
      .then((result) => {
        if (cancelled) return;
        setProject(result);
        setState("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, [token, projectId, reloadToken]);

  function retry() {
    setState("loading");
    setReloadToken((count) => count + 1);
  }

  async function handleUpdate(values: { name: string; description: string }) {
    if (!token) return;
    const updated = await updateProject(token, projectId, {
      name: values.name,
      description: values.description || undefined,
    });
    setProject(updated);
    setEditing(false);
    push("Project updated.", "success");
  }

  async function handleArchive() {
    if (!token) return;
    setConfirmingArchive(false);
    try {
      const archived = await archiveProject(token, projectId);
      setProject(archived);
      push("Project archived.", "success");
    } catch {
      push("Could not archive project.", "error");
    }
  }

  if (state === "loading") {
    return (
      <div
        className="flex items-center justify-center py-16"
        role="status"
        aria-label="Loading project"
      >
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900 dark:border-zinc-700 dark:border-t-zinc-50" />
      </div>
    );
  }

  if (state === "error" || project === null) {
    return (
      <ErrorState
        message="Could not load this project."
        retryable
        onRetry={retry}
      />
    );
  }

  return (
    <div className="flex max-w-2xl flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            {project.name}
          </h1>
          <ProjectStatusBadge status={project.status} />
        </div>
        <div className="flex shrink-0 gap-2">
          {!editing ? (
            <Button variant="secondary" onClick={() => setEditing(true)}>
              Edit
            </Button>
          ) : null}
          {project.status !== "archived" ? (
            <Button variant="danger" onClick={() => setConfirmingArchive(true)}>
              Archive
            </Button>
          ) : null}
        </div>
      </div>

      {editing ? (
        <ProjectForm
          initialName={project.name}
          initialDescription={project.description ?? ""}
          submitLabel="Save changes"
          onSubmit={handleUpdate}
        />
      ) : (
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          {project.description || "No description."}
        </p>
      )}

      <ConfirmDialog
        open={confirmingArchive}
        title="Archive this project?"
        description="Archived projects can't start new collection jobs."
        confirmLabel="Archive project"
        onConfirm={handleArchive}
        onCancel={() => setConfirmingArchive(false)}
      />
    </div>
  );
}
