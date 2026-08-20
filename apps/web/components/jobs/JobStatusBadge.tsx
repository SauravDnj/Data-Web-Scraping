/** The 8 `app.domain.jobs.JobStatus` values (backend), rendered
 * consistently anywhere a job's status appears. Colors are decorative
 * only — the text label itself is what actually conveys status, so
 * this never breaks for a screen reader or a color-blind user. */
const STATUS_STYLES: Record<string, string> = {
  draft:
    "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
  queued:
    "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300",
  running:
    "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300",
  paused:
    "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300",
  completed:
    "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300",
  partially_completed:
    "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-300",
  cancelled:
    "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400",
};

function label(status: string): string {
  return status
    .split("_")
    .map((word) => word[0]?.toUpperCase() + word.slice(1))
    .join(" ");
}

export function JobStatusBadge({ status }: { status: string }) {
  const className =
    STATUS_STYLES[status] ??
    "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300";
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}
    >
      {label(status)}
    </span>
  );
}
