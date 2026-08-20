import { afterEach, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AuthProvider } from "../../lib/auth/AuthContext";
import { ToastProvider } from "../../components/feedback/Toast";
import NewProjectPage from "../../app/(app)/projects/new/page";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

afterEach(() => {
  vi.unstubAllGlobals();
  window.sessionStorage.clear();
  push.mockClear();
});

test("creating a project redirects to its detail page", async () => {
  window.sessionStorage.setItem("gmdp.session_token", "tok-123");
  const fetchMock = vi.fn().mockImplementation((input: RequestInfo | URL, init) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) {
      return Promise.resolve(
        jsonResponse({
          data: { id: 1, email: "owner@example.com", status: "active" },
          request_id: "req-me",
        }),
      );
    }
    if (url.endsWith("/projects") && init?.method === "POST") {
      const body = JSON.parse(String(init.body));
      expect(body.name).toBe("Coffee Shops NYC");
      expect(body.source_type).toBe("google_maps");
      return Promise.resolve(
        jsonResponse({
          data: {
            id: 42,
            name: "Coffee Shops NYC",
            source_type: "google_maps",
            status: "active",
            description: null,
            created_at: null,
            updated_at: null,
          },
          request_id: "req-create",
        }),
      );
    }
    throw new Error(`unexpected fetch to ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);

  render(
    <AuthProvider>
      <ToastProvider>
        <NewProjectPage />
      </ToastProvider>
    </AuthProvider>,
  );

  fireEvent.change(await screen.findByLabelText("Name"), {
    target: { value: "Coffee Shops NYC" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Create project" }));

  await waitFor(() => expect(push).toHaveBeenCalledWith("/projects/42"));
});
