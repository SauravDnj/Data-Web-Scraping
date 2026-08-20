import { EmptyState } from "@/components/feedback/EmptyState";

export default function RecordsPage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Records
      </h1>
      <EmptyState
        title="No records yet"
        description="Create a project configuration and run a collection job."
      />
    </div>
  );
}
