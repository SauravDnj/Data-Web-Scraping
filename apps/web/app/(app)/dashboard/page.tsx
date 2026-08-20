import { EmptyState } from "@/components/feedback/EmptyState";

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Dashboard
      </h1>
      <EmptyState
        title="No activity yet"
        description="Job and record metrics appear here once a project has run a collection job."
      />
    </div>
  );
}
