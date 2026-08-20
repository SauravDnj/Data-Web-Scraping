import { expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { ErrorState } from "../../components/feedback/ErrorState";

test("shows the failure message and a retry action when retryable", () => {
  const onRetry = vi.fn();
  render(
    <ErrorState message="Failed to load jobs." retryable onRetry={onRetry} />,
  );

  expect(screen.getByRole("alert")).toHaveTextContent("Failed to load jobs.");
  const retryButton = screen.getByRole("button", { name: "Retry" });
  fireEvent.click(retryButton);
  expect(onRetry).toHaveBeenCalledOnce();
});

test("omits the retry action when the failure is not retryable", () => {
  render(<ErrorState message="Configuration is invalid." retryable={false} />);

  expect(
    screen.queryByRole("button", { name: "Retry" }),
  ).not.toBeInTheDocument();
  expect(screen.getByRole("alert")).toHaveTextContent(/will not resolve/i);
});
