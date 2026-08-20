import { Button } from "@/components/ui/Button";

/**
 * docs/06_UI_DEEP.md's "Error state" spec, for a caught/handled API
 * failure inside a page (a failed list fetch, a rejected action) —
 * distinct from `app/error.tsx`/`app/global-error.tsx`, which only
 * catch uncaught render-time exceptions. Shows what failed, whether
 * it's retryable, and the recommended next action; never a raw stack
 * trace or exception message straight from the network layer.
 */
export function ErrorState({
  title = "Something went wrong",
  message,
  retryable = true,
  onRetry,
}: {
  title?: string;
  message: string;
  retryable?: boolean;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center justify-center gap-3 rounded-lg border border-red-200 bg-red-50 px-6 py-12 text-center dark:border-red-900/50 dark:bg-red-950/30"
    >
      <h3 className="text-sm font-semibold text-red-900 dark:text-red-200">
        {title}
      </h3>
      <p className="max-w-sm text-sm text-red-700 dark:text-red-300">
        {message}
      </p>
      <p className="text-xs text-red-500 dark:text-red-400">
        {retryable
          ? "This looks temporary — try again."
          : "This will not resolve on its own; check the details before retrying."}
      </p>
      {retryable && onRetry ? (
        <Button variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}
