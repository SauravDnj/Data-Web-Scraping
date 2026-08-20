"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthContext";
import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  const { status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") {
      router.replace("/dashboard");
    }
  }, [status, router]);

  if (status !== "unauthenticated") {
    return (
      <div
        className="flex flex-1 items-center justify-center"
        role="status"
        aria-label="Checking session"
      >
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900 dark:border-zinc-700 dark:border-t-zinc-50" />
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm rounded-lg border border-zinc-200 p-6 dark:border-zinc-800">
        <h1 className="mb-6 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Sign in
        </h1>
        <LoginForm />
      </div>
    </div>
  );
}
