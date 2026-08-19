"use client";

import { useEffect } from "react";

export default function ErrorPage({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="max-w-md text-zinc-600 dark:text-zinc-400">
        An unexpected error occurred. You can try again, or reload the page.
      </p>
      <button
        type="button"
        onClick={() => retry()}
        className="rounded-full bg-foreground px-5 py-2 text-sm font-medium text-background"
      >
        Try again
      </button>
    </div>
  );
}
