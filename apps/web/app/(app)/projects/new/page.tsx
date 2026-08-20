"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthContext";
import { createProject } from "@/lib/api/projects";
import { useToast } from "@/components/feedback/Toast";
import { ProjectForm } from "@/components/projects/ProjectForm";

// V1 supports exactly one provider (docs/16_MEMORY.md's "Resolved
// design decisions" / SUPPORTED_PROVIDERS in app.services.configs) —
// not exposed as a choice here, matching "no detailed business forms
// yet" (T070/T072's own scope boundary). A provider picker becomes
// meaningful once a second provider actually exists.
const SOURCE_TYPE = "google_maps";

export default function NewProjectPage() {
  const { token } = useAuth();
  const { push } = useToast();
  const router = useRouter();

  async function handleSubmit(values: { name: string; description: string }) {
    if (!token) return;
    const created = await createProject(token, {
      name: values.name,
      source_type: SOURCE_TYPE,
      description: values.description || undefined,
    });
    push("Project created.", "success");
    router.push(`/projects/${created.id}`);
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        New Project
      </h1>
      <div className="max-w-md">
        <ProjectForm submitLabel="Create project" onSubmit={handleSubmit} />
      </div>
    </div>
  );
}
