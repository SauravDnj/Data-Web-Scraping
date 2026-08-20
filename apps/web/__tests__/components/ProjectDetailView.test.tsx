import { afterEach, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AuthProvider } from "../../lib/auth/AuthContext";
import { ToastProvider } from "../../components/feedback/Toast";
import { ProjectDetailView } from "../../components/projects/ProjectDetailView";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

const baseProject = {
  id: 7,
  name: "Coffee Shops NYC",
  source_type: "google_maps",
  status: "active",
  description: "Weekly scan",
  created_at: null,
  updated_at: null,
};

function renderDetailView() {
  return render(
    <AuthProvider>
      <ToastProvider>
        <ProjectDetailView projectId={7} />
      </ToastProvider>
    </AuthProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  window.sessionStorage.clear();
});

test("loads and renders the project's name, status, and description", async () => {
  window.sessionStorage.setItem("gmdp.session_token", "tok-123");
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) {
        return Promise.resolve(
          jsonResponse({
            data: { id: 1, email: "owner@example.com", status: "active" },
            request_id: "req-me",
          }),
        );
      }
      if (url.endsWith("/projects/7")) {
        return Promise.resolve(
          jsonResponse({ data: baseProject, request_id: "req-project" }),
        );
      }
      throw new Error(`unexpected fetch to ${url}`);
    }),
  );

  renderDetailView();

  expect(await screen.findByText("Coffee Shops NYC")).toBeInTheDocument();
  expect(screen.getByText("active")).toBeInTheDocument();
  expect(screen.getByText("Weekly scan")).toBeInTheDocument();
});

test("archiving requires confirmation before the request is sent", async () => {
  window.sessionStorage.setItem("gmdp.session_token", "tok-123");
  const archiveCall = vi.fn();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((input: RequestInfo | URL, init) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) {
        return Promise.resolve(
          jsonResponse({
            data: { id: 1, email: "owner@example.com", status: "active" },
            request_id: "req-me",
          }),
        );
      }
      if (url.endsWith("/projects/7") && init?.method === "DELETE") {
        archiveCall();
        return Promise.resolve(
          jsonResponse({
            data: { ...baseProject, status: "archived" },
            request_id: "req-archive",
          }),
        );
      }
      if (url.endsWith("/projects/7")) {
        return Promise.resolve(
          jsonResponse({ data: baseProject, request_id: "req-project" }),
        );
      }
      throw new Error(`unexpected fetch to ${url}`);
    }),
  );

  renderDetailView();
  await screen.findByText("Coffee Shops NYC");

  fireEvent.click(screen.getByRole("button", { name: "Archive" }));
  expect(archiveCall).not.toHaveBeenCalled(); // confirmation not yet given

  fireEvent.click(screen.getByRole("button", { name: "Archive project" }));
  await waitFor(() => expect(archiveCall).toHaveBeenCalledOnce());
  expect(await screen.findByText("archived")).toBeInTheDocument();
});
