"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth/AuthContext";
import {
  fetchJobSummary,
  fetchJobs,
  fetchRecordCount,
  type JobListItem,
  type JobSummary,
} from "@/lib/api/dashboard";
import { StatCard } from "@/components/dashboard/StatCard";
import { RecentJobsTable } from "@/components/dashboard/RecentJobsTable";
import { EmptyState } from "@/components/feedback/EmptyState";
import { ErrorState } from "@/components/feedback/ErrorState";

const RECENT_LIMIT = 5;

type LoadState = "loading" | "error" | "ready";

/** docs/06_UI_DEEP.md's dashboard spec: 4 cards (Active/Completed/
 * Failed Jobs, Records) + a recent-activity table + recent failures.
 * Every number here comes straight from the backend
 * (`GET /jobs/summary`, `GET /records/count`, `GET /jobs`) — never
 * derived from a partial page of results client-side (T071's own DO
 * NOT rule). Works identically against an empty DB (every count 0,
 * both lists show their EmptyState) and a populated one, per T071's
 * literal acceptance criterion. */
export default function DashboardPage() {
  const { token } = useAuth();
  const [state, setState] = useState<LoadState>("loading");
  const [summary, setSummary] = useState<JobSummary | null>(null);
  const [recordTotal, setRecordTotal] = useState(0);
  const [recentJobs, setRecentJobs] = useState<JobListItem[]>([]);
  const [recentFailures, setRecentFailures] = useState<JobListItem[]>([]);
  // Bumped by `retry()` to re-run the effect below — matches
  // `AuthContext.tsx`'s own working shape for this same
  // react-hooks/set-state-in-effect constraint: the effect's setState
  // calls must be written as inline `.then()`/`.catch()` callbacks,
  // not routed through a separately-named function the effect merely
  // calls, or the linter's static trace flags it regardless of the
  // `await` in between.
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    Promise.all([
      fetchJobSummary(token),
      fetchRecordCount(token),
      fetchJobs(token, { limit: RECENT_LIMIT }),
      fetchJobs(token, { status: "failed", limit: RECENT_LIMIT }),
    ])
      .then(([summaryResult, recordsResult, recentResult, failuresResult]) => {
        if (cancelled) return;
        setSummary(summaryResult);
        setRecordTotal(recordsResult.total);
        setRecentJobs(recentResult.items);
        setRecentFailures(failuresResult.items);
        setState("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, [token, reloadToken]);

  function retry() {
    setState("loading");
    setReloadToken((count) => count + 1);
  }

  if (state === "loading") {
    return (
      <div
        className="flex flex-1 items-center justify-center py-16"
        role="status"
        aria-label="Loading dashboard"
      >
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900 dark:border-zinc-700 dark:border-t-zinc-50" />
      </div>
    );
  }

  if (state === "error" || summary === null) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Dashboard
        </h1>
        <ErrorState
          message="Could not load dashboard metrics."
          retryable
          onRetry={retry}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Dashboard
      </h1>

      <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Active Jobs" value={summary.active_jobs} />
        <StatCard label="Completed Jobs" value={summary.completed_jobs} />
        <StatCard label="Failed Jobs" value={summary.failed_jobs} />
        <StatCard label="Records" value={recordTotal} />
      </dl>

      <section className="flex flex-col gap-2">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
          Recent activity
        </h2>
        {recentJobs.length === 0 ? (
          <EmptyState
            title="No activity yet"
            description="Job and record metrics appear here once a project has run a collection job."
          />
        ) : (
          <RecentJobsTable jobs={recentJobs} />
        )}
      </section>

      <section className="flex flex-col gap-2">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
          Recent failures
        </h2>
        {recentFailures.length === 0 ? (
          <EmptyState
            title="No failures"
            description="Failed jobs show up here for quick triage."
          />
        ) : (
          <RecentJobsTable jobs={recentFailures} />
        )}
      </section>
    </div>
  );
}
