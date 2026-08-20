import { afterEach, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AuthProvider } from "../../lib/auth/AuthContext";
import { ToastProvider } from "../../components/feedback/Toast";
import { LoginForm } from "../../components/auth/LoginForm";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

function renderLoginForm() {
  return render(
    <AuthProvider>
      <ToastProvider>
        <LoginForm />
      </ToastProvider>
    </AuthProvider>,
  );
}

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

afterEach(() => {
  vi.unstubAllGlobals();
  replace.mockClear();
  window.sessionStorage.clear();
});

test("a successful login redirects to the dashboard", async () => {
  const fetchMock = vi.fn().mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/auth/login")) {
      return Promise.resolve(
        jsonResponse({
          data: { token: "tok-123", expires_at: "2026-08-20T12:00:00Z" },
          request_id: "req-1",
        }),
      );
    }
    if (url.endsWith("/auth/me")) {
      return Promise.resolve(
        jsonResponse({
          data: { id: 1, email: "owner@example.com", status: "active" },
          request_id: "req-2",
        }),
      );
    }
    throw new Error(`unexpected fetch to ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);

  // sessionStorage isn't present on the AuthProvider's initial mount
  // in this test — it starts unauthenticated, matching a fresh visit.
  renderLoginForm();

  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: "owner@example.com" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "correct horse battery staple" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

  await waitFor(() => expect(replace).toHaveBeenCalledWith("/dashboard"));
});

test("an invalid login shows a same-message error, not the raw failure", async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse(
      { error: { message: "Invalid email or password." }, request_id: "req-1" },
      401,
    ),
  );
  vi.stubGlobal("fetch", fetchMock);

  renderLoginForm();

  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: "owner@example.com" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "wrong" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Incorrect email or password.",
  );
  expect(replace).not.toHaveBeenCalled();
});
