# UI File Plan

Recommended Next.js structure:

``` text
apps/web/
├── app/
│   ├── page.tsx
│   ├── dashboard/
│   ├── projects/
│   │   ├── page.tsx
│   │   ├── new/
│   │   └── [projectId]/
│   │       ├── page.tsx
│   │       ├── configuration/
│   │       ├── jobs/
│   │       ├── records/
│   │       └── exports/
│   ├── jobs/
│   ├── records/
│   ├── schedules/
│   └── settings/
├── components/
│   ├── layout/
│   ├── projects/
│   ├── jobs/
│   ├── records/
│   ├── forms/
│   └── feedback/
├── lib/
│   ├── api/
│   ├── validation/
│   └── formatting/
└── tests/
```

## UI implementation order

1.  app shell;
2.  dashboard;
3.  projects;
4.  configuration wizard;
5.  jobs;
6.  records;
7.  exports;
8.  schedules;
9.  settings.

Do not build every screen before connecting the first vertical workflow.
