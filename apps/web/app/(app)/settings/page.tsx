"use client";

import { useAuth } from "@/lib/auth/AuthContext";
import { EmptyState } from "@/components/feedback/EmptyState";

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Settings
      </h1>
      {user ? (
        <div className="rounded-lg border border-zinc-200 p-4 text-sm dark:border-zinc-800">
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
            <dt className="text-zinc-500 dark:text-zinc-400">Email</dt>
            <dd className="text-zinc-900 dark:text-zinc-50">{user.email}</dd>
            <dt className="text-zinc-500 dark:text-zinc-400">Account status</dt>
            <dd className="text-zinc-900 dark:text-zinc-50">{user.status}</dd>
          </dl>
        </div>
      ) : null}
      <EmptyState
        title="Nothing to configure yet"
        description="Provider credentials, budgets, and account preferences land here in later tasks."
      />
    </div>
  );
}
