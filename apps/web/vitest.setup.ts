import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// vitest.config.mts does not set `test.globals`, so @testing-library/
// react's automatic per-test cleanup (which detects a global
// `afterEach`) never registers itself — without this, elements from
// an earlier test in the same file leak into later tests' DOM queries.
afterEach(() => {
  cleanup();
});

// jsdom implements <dialog>'s `open` attribute reflection but not the
// imperative showModal()/close() methods (confirmed against the
// jsdom version this project pins) — every real browser supports
// both, so this is a test-environment gap, not a component bug.
// Minimal polyfill so any component using <dialog> (e.g.
// components/ui/ConfirmDialog.tsx, T072) is testable.
if (typeof HTMLDialogElement !== "undefined") {
  if (!HTMLDialogElement.prototype.showModal) {
    HTMLDialogElement.prototype.showModal = function (this: HTMLDialogElement) {
      this.setAttribute("open", "");
    };
  }
  if (!HTMLDialogElement.prototype.close) {
    HTMLDialogElement.prototype.close = function (this: HTMLDialogElement) {
      this.removeAttribute("open");
      this.dispatchEvent(new Event("close"));
    };
  }
}
