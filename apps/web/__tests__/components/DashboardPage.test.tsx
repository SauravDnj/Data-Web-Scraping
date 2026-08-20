import { afterEach, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AuthProvider } from "../../lib/auth/AuthContext";
import DashboardPage from "../../app/(app)/dashboard/page";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

afterEach(() => {
  vi.unstubAllGlobals();
  window.sessionStorage.clear();
});

function stubAuthenticatedFetch(
  onJobsRequest: (url: string) => Response,
) {
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
    if (url.includes("/records/count")) {
      return Promise.resolve(
        jsonResponse({ data: { total: 42 }, request_id: "req-count" }),
      );
    }
    if (url.endsWith("/jobs/summary")) {
      return Promise.resolve(
        jsonResponse({
          data: { active_jobs: 2, completed_jobs: 5, failed_jobs: 1 },
          request_id: "req-summary",
        }),
      );
    }
    if (url.includes("/jobs")) {
      return Promise.resolve(onJobsRequest(url));
    }
    throw new Error(`unexpected fetch to ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

test("renders the four dashboard cards from real backend numbers", async () => {
  stubAuthenticatedFetch((url) =>
    jsonResponse({
      data: { items: [], total: 0, limit: 5, offset: 0 },
      request_id: `req-${url}`,
    }),
  );

  render(
    <AuthProvider>
      <DashboardPage />
    </AuthProvider>,
  );

  expect(await screen.findByText("2")).toBeInTheDocument(); // Active Jobs
  expect(screen.getByText("5")).toBeInTheDocument(); // Completed Jobs
  expect(screen.getByText("1")).toBeInTheDocument(); // Failed Jobs
  expect(screen.getByText("42")).toBeInTheDocument(); // Records
});

test("shows the empty state when there is no recent activity", async () => {
  stubAuthenticatedFetch((url) =>
    jsonResponse({
      data: { items: [], total: 0, limit: 5, offset: 0 },
      request_id: `req-${url}`,
    }),
  );

  render(
    <AuthProvider>
      <DashboardPage />
    </AuthProvider>,
  );

  expect(await screen.findByText("No activity yet")).toBeInTheDocument();
  expect(screen.getByText("No failures")).toBeInTheDocument();
});

test("renders the recent-activity table when jobs exist", async () => {
  stubAuthenticatedFetch((url) => {
    if (url.includes("status=failed")) {
      return jsonResponse({
        data: { items: [], total: 0, limit: 5, offset: 0 },
        request_id: "req-failed",
      });
    }
    return jsonResponse({
      data: {
        items: [
          {
            id: 7,
            project_id: 3,
            status: "completed",
            counters: {
              total_units: 10,
              successful_units: 10,
              failed_units: 0,
              skipped_units: 0,
              records_created: 8,
              records_updated: 2,
              records_rejected: 0,
            },
            requested_at: "2026-08-20T12:00:00Z",
            started_at: "2026-08-20T12:00:01Z",
            finished_at: "2026-08-20T12:01:00Z",
            error_code: null,
            error_message: null,
          },
        ],
        total: 1,
        limit: 5,
        offset: 0,
      },
      request_id: "req-recent",
    });
  });

  render(
    <AuthProvider>
      <DashboardPage />
    </AuthProvider>,
  );

  expect(await screen.findByText("#7")).toBeInTheDocument();
  expect(screen.getByText("Project #3")).toBeInTheDocument();
  expect(screen.getByText("Completed")).toBeInTheDocument();
  expect(screen.getByText("10")).toBeInTheDocument(); // 8 created + 2 updated
});

test("shows an error state with a retry action when a fetch fails", async () => {
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
      <DashboardPage />
    </AuthProvider>,
  );

  expect(
    await screen.findByText("Could not load dashboard metrics."),
  ).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
});
