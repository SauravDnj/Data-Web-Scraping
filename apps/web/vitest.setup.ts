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
