import { expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import { EmptyState } from "../../components/feedback/EmptyState";

test("renders the title and description", () => {
  render(
    <EmptyState
      title="No records yet"
      description="Create a project configuration and run a collection job."
    />,
  );

  expect(
    screen.getByRole("heading", { name: "No records yet" }),
  ).toBeInTheDocument();
  expect(
    screen.getByText(/create a project configuration/i),
  ).toBeInTheDocument();
});

test("renders an optional action", () => {
  render(
    <EmptyState
      title="No projects yet"
      description="Create one to get started."
      action={<button>New project</button>}
    />,
  );

  expect(
    screen.getByRole("button", { name: "New project" }),
  ).toBeInTheDocument();
});
