import { expect, test } from "vitest";
import { apiBaseUrl } from "../lib/api/config";

test("apiBaseUrl falls back to a local default when unset", () => {
  expect(apiBaseUrl).toBe("http://localhost:8000/api/v1");
});
