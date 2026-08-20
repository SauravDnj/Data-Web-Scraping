import { expect, test, vi } from "vitest";
import Page from "../app/page";

const redirect = vi.fn();
vi.mock("next/navigation", () => ({ redirect: (path: string) => redirect(path) }));

test("the root route redirects into the app rather than rendering content", () => {
  Page();
  expect(redirect).toHaveBeenCalledWith("/dashboard");
});
