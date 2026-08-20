"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthContext";
import { useToast } from "@/components/feedback/Toast";
import { Button } from "@/components/ui/Button";

export function TopNav({ onOpenMobileNav }: { onOpenMobileNav: () => void }) {
  const { user, logout } = useAuth();
  const { push } = useToast();
  const router = useRouter();

  async function handleSignOut() {
    await logout();
    push("Signed out.", "info");
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between gap-4 border-b border-zinc-200 bg-white/80 px-4 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80">
      <button
        type="button"
        onClick={onOpenMobileNav}
        aria-label="Open navigation menu"
        className="rounded-md p-2 text-zinc-600 hover:bg-zinc-100 md:hidden dark:text-zinc-400 dark:hover:bg-zinc-800"
      >
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          className="h-5 w-5"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <div className="flex-1" />

      <div className="flex items-center gap-3">
        {user ? (
          <span className="hidden truncate text-sm text-zinc-600 sm:inline dark:text-zinc-400">
            {user.email}
          </span>
        ) : null}
        <Button variant="secondary" onClick={handleSignOut}>
          Sign out
        </Button>
      </div>
    </header>
  );
}
