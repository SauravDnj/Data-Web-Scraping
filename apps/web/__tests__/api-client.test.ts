import { afterEach, expect, test, vi } from "vitest";
import { apiFetch } from "../lib/api/client";

afterEach(() => {
  vi.unstubAllGlobals();
});

test("returns the unwrapped data on a successful envelope response", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ data: { id: 1 }, request_id: "req-1" }),
        { status: 200 },
      ),
    ),
  );

  const result = await apiFetch<{ id: number }>("/projects/1");
  expect(result).toEqual({ id: 1 });
});

test("throws ApiError with the server's message on an error envelope", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error: { message: "Not found." },
          request_id: "req-2",
        }),
        { status: 404 },
      ),
    ),
  );

  await expect(apiFetch("/projects/999")).rejects.toMatchObject({
    name: "ApiError",
    message: "Not found.",
    status: 404,
    requestId: "req-2",
  });
});

test("a 204 response (e.g. logout) resolves without parsing a body", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(new Response(null, { status: 204 })),
  );

  await expect(apiFetch("/auth/logout", { method: "POST" })).resolves.toBeUndefined();
});
