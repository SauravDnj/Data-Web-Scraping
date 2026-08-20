import { EmptyState } from "@/components/feedback/EmptyState";

export default function JobsPage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Jobs
      </h1>
      <EmptyState
        title="No jobs yet"
        description="Jobs appear here once a project's configuration starts a collection run."
      />
    </div>
  );
}
