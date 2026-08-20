"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthContext";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopNav } from "@/components/layout/TopNav";

/**
 * The auth-aware shell (T070 item 4): every route nested under this
 * route group requires a session. `useAuth()`'s `status` starts
 * `"loading"` while a stored token (if any) is validated against
 * `GET /auth/me` — the shell must not flash its content, then yank
 * the user to `/login`, so it renders a neutral loading state until
 * that check resolves.
 */
export default function AppShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { status } = useAuth();
  const router = useRouter();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [status, router]);

  if (status !== "authenticated") {
    return (
      <div
        className="flex min-h-screen flex-1 items-center justify-center"
        role="status"
        aria-label="Checking session"
      >
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900 dark:border-zinc-700 dark:border-t-zinc-50" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar
        mobileOpen={mobileNavOpen}
        onCloseMobile={() => setMobileNavOpen(false)}
      />
      <div className="flex min-h-screen flex-1 flex-col">
        <TopNav onOpenMobileNav={() => setMobileNavOpen(true)} />
        <main className="flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
