import { JobListItem } from "@/lib/api/dashboard";
import { JobStatusBadge } from "@/components/jobs/JobStatusBadge";

/** docs/06_UI_DEEP.md's "Recent activity" table:
 * `Project | Job | Status | Records | Time`. "Project" shows a
 * project id, not a name — `GET /projects` doesn't exist yet (T072
 * owns it); swap this for a real name once that route lands rather
 * than joining it in here ahead of that task. */
export function RecentJobsTable({ jobs }: { jobs: JobListItem[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-zinc-200 text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
          <tr>
            <th className="px-4 py-2 font-medium">Project</th>
            <th className="px-4 py-2 font-medium">Job</th>
            <th className="px-4 py-2 font-medium">Status</th>
            <th className="px-4 py-2 font-medium">Records</th>
            <th className="px-4 py-2 font-medium">Time</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {jobs.map((job) => (
            <tr key={job.id}>
              <td className="px-4 py-2 text-zinc-600 dark:text-zinc-400">
                Project #{job.project_id}
              </td>
              <td className="px-4 py-2 text-zinc-900 dark:text-zinc-50">
                #{job.id}
              </td>
              <td className="px-4 py-2">
                <JobStatusBadge status={job.status} />
              </td>
              <td className="px-4 py-2 text-zinc-600 dark:text-zinc-400">
                {(
                  job.counters.records_created + job.counters.records_updated
                ).toLocaleString()}
              </td>
              <td className="px-4 py-2 text-zinc-600 dark:text-zinc-400">
                {job.requested_at
                  ? new Date(job.requested_at).toLocaleString()
                  : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
