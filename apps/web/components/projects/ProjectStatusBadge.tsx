const STATUS_STYLES: Record<string, string> = {
  active:
    "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300",
  archived: "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400",
};

export function ProjectStatusBadge({ status }: { status: string }) {
  const className =
    STATUS_STYLES[status] ??
    "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300";
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${className}`}
    >
      {status}
    </span>
  );
}
