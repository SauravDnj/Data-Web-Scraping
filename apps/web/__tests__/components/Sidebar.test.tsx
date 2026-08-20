import { expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Sidebar } from "../../components/layout/Sidebar";

vi.mock("next/navigation", () => ({
  usePathname: () => "/jobs",
}));

test("marks the nav item matching the current path as active", () => {
  render(<Sidebar mobileOpen={false} onCloseMobile={() => {}} />);

  const jobsLink = screen.getByRole("link", { name: "Jobs" });
  expect(jobsLink).toHaveAttribute("aria-current", "page");

  const projectsLink = screen.getByRole("link", { name: "Projects" });
  expect(projectsLink).not.toHaveAttribute("aria-current");
});

test("renders every top-level nav item", () => {
  render(<Sidebar mobileOpen={false} onCloseMobile={() => {}} />);

  for (const label of [
    "Dashboard",
    "Projects",
    "Jobs",
    "Records",
    "Schedules",
    "Settings",
  ]) {
    expect(screen.getByRole("link", { name: label })).toBeInTheDocument();
  }
});
