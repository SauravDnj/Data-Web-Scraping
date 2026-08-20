import { type ReactNode } from "react";

/**
 * docs/06_UI_DEEP.md's "Empty state" spec — explain what to do, e.g.
 * "No records yet. Create a project configuration and run a
 * collection job." Every list/table screen (projects, jobs, records,
 * schedules) should reach for this rather than inventing its own
 * blank-slate copy.
 */
export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-zinc-300 px-6 py-16 text-center dark:border-zinc-700">
      <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
        {title}
      </h3>
      <p className="max-w-sm text-sm text-zinc-500 dark:text-zinc-400">
        {description}
      </p>
      {action}
    </div>
  );
}
