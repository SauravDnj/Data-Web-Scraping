# apps/web

Next.js + TypeScript frontend. Presentation layer only — no secrets, no
direct database access. Talks to `apps/api` over HTTP via
`lib/api/client.ts`.

Business screens (dashboard, projects, jobs, records, exports,
schedules, settings) land in later tasks (T070+) following
`docs/23_UI_FILE_PLAN.md`. This app currently has only the shell: root
layout, a placeholder home page, error/loading UI, and the API client
boundary, from T011.

## Setup

```bash
cp .env.example .env.local   # if you need to override the API base URL
npm install
```

## Commands

```bash
npm run dev         # development server, http://localhost:3000
npm run build        # production build
npm run start          # run the production build
npm run lint             # ESLint
npm run typecheck         # tsc --noEmit
npm test                   # vitest (single run)
npm run test:watch          # vitest (watch mode)
```

## Configuration

`NEXT_PUBLIC_API_BASE_URL` — base URL of the backend API. Safe to
expose to the browser (prefixed `NEXT_PUBLIC_`). See
`lib/api/config.ts`. Any future server-only configuration must go in a
separate module guarded by the `server-only` package — never add
non-`NEXT_PUBLIC_` values to a file imported by client components.
