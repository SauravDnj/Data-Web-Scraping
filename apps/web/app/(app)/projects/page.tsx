import { EmptyState } from "@/components/feedback/EmptyState";

export default function ProjectsPage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Projects
      </h1>
      <EmptyState
        title="No projects yet"
        description="Create a project to configure a Google Maps data collection source."
      />
    </div>
  );
}
