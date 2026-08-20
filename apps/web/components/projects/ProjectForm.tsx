"use client";

import { useState, type FormEvent } from "react";
import { ApiError } from "@/lib/api/client";
import { Button } from "@/components/ui/Button";

export function ProjectForm({
  initialName = "",
  initialDescription = "",
  submitLabel,
  onSubmit,
}: {
  initialName?: string;
  initialDescription?: string;
  submitLabel: string;
  onSubmit: (values: { name: string; description: string }) => Promise<void>;
}) {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setPending(true);
    try {
      await onSubmit({ name, description });
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Something went wrong. Try again.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="project-name"
          className="text-sm font-medium text-zinc-700 dark:text-zinc-300"
        >
          Name
        </label>
        <input
          id="project-name"
          name="name"
          required
          value={name}
          onChange={(event) => setName(event.target.value)}
          className="rounded-md border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 dark:border-zinc-700 dark:bg-zinc-900"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="project-description"
          className="text-sm font-medium text-zinc-700 dark:text-zinc-300"
        >
          Description (optional)
        </label>
        <textarea
          id="project-description"
          name="description"
          rows={3}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          className="rounded-md border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 dark:border-zinc-700 dark:bg-zinc-900"
        />
      </div>

      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}

      <Button type="submit" disabled={pending} className="self-start">
        {pending ? "Saving…" : submitLabel}
      </Button>
    </form>
  );
}
