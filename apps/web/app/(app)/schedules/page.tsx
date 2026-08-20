import { EmptyState } from "@/components/feedback/EmptyState";

export default function SchedulesPage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Schedules
      </h1>
      <EmptyState
        title="No schedules yet"
        description="Schedules let a project's configuration run automatically on a recurring basis."
      />
    </div>
  );
}
