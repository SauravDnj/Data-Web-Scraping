/** docs/06_UI_DEEP.md's page tree — the six top-level app routes,
 * shared between the sidebar and any future breadcrumb/mobile nav. */
export const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/projects", label: "Projects" },
  { href: "/jobs", label: "Jobs" },
  { href: "/records", label: "Records" },
  { href: "/schedules", label: "Schedules" },
  { href: "/settings", label: "Settings" },
] as const;
