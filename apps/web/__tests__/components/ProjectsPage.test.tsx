import { afterEach, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AuthProvider } from "../../lib/auth/AuthContext";
import ProjectsPage from "../../app/(app)/projects/page";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

afterEach(() => {
  vi.unstubAllGlobals();
  window.sessionStorage.clear();
});

function stubAuthenticatedFetch(projectsResponse: Response) {
  window.sessionStorage.setItem("gmdp.session_token", "tok-123");
  const fetchMock = vi.fn().mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) {
      return Promise.resolve(
        jsonResponse({
          data: { id: 1, email: "owner@example.com", status: "active" },
          request_id: "req-me",
        }),
      );
    }
    if (url.endsWith("/projects")) {
      return Promise.resolve(projectsResponse);
    }
    throw new Error(`unexpected fetch to ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
}

test("shows the empty state with a call to action when there are no projects", async () => {
  stubAuthenticatedFetch(
    jsonResponse({
      data: { items: [], total: 0, limit: 50, offset: 0 },
      request_id: "req-projects",
    }),
  );

  render(
    <AuthProvider>
      <ProjectsPage />
    </AuthProvider>,
  );

  expect(await screen.findByText("No projects yet")).toBeInTheDocument();
  expect(screen.getAllByRole("link", { name: "New Project" })).toHaveLength(2);
});

test("renders a row per project with its status", async () => {
  stubAuthenticatedFetch(
    jsonResponse({
      data: {
        items: [
          {
            id: 1,
            name: "Coffee Shops NYC",
            source_type: "google_maps",
            status: "active",
            description: null,
            created_at: null,
            updated_at: null,
          },
        ],
        total: 1,
        limit: 50,
        offset: 0,
      },
      request_id: "req-projects",
    }),
  );

  render(
    <AuthProvider>
      <ProjectsPage />
    </AuthProvider>,
  );

  expect(await screen.findByText("Coffee Shops NYC")).toBeInTheDocument();
  expect(screen.getByText("active")).toBeInTheDocument();
});

test("shows an error state with retry when the request fails", async () => {
  window.sessionStorage.setItem("gmdp.session_token", "tok-123");
  const fetchMock = vi.fn().mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) {
      return Promise.resolve(
        jsonResponse({
          data: { id: 1, email: "owner@example.com", status: "active" },
          request_id: "req-me",
        }),
      );
    }
    return Promise.resolve(
      jsonResponse({ error: { message: "boom" }, request_id: "req-err" }, 500),
    );
  });
  vi.stubGlobal("fetch", fetchMock);

  render(
    <AuthProvider>
      <ProjectsPage />
    </AuthProvider>,
  );

  expect(await screen.findByText("Could not load projects.")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
});
