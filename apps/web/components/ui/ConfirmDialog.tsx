"use client";

import { useEffect, useRef } from "react";
import { Button } from "./Button";

/** A native `<dialog>` (built-in focus trap, ESC-to-close, and
 * `::backdrop`) for confirming a destructive/state-changing action —
 * e.g. archiving a project (T072 item 9: "confirm destructive/archive
 * action"). Controlled by `open`; this component never holds its own
 * open/closed state. */
export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      onCancel={onCancel}
      onClose={onCancel}
      className="rounded-lg border border-zinc-200 bg-white p-0 backdrop:bg-black/30 dark:border-zinc-800 dark:bg-zinc-900"
    >
      <div className="flex w-80 flex-col gap-4 p-6">
        <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">
          {title}
        </h2>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">{description}</p>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button variant="danger" onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </dialog>
  );
}
