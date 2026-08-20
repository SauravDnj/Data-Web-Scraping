import { expect, test } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { ToastProvider, useToast } from "../../components/feedback/Toast";

function PushButton({ message }: { message: string }) {
  const { push } = useToast();
  return <button onClick={() => push(message, "success")}>Push</button>;
}

test("pushing a toast renders it, and dismissing removes it", () => {
  render(
    <ToastProvider>
      <PushButton message="Signed in." />
    </ToastProvider>,
  );

  expect(screen.queryByText("Signed in.")).not.toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Push" }));
  expect(screen.getByText("Signed in.")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Dismiss notification" }));
  expect(screen.queryByText("Signed in.")).not.toBeInTheDocument();
});
