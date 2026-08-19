/**
 * Client-safe API configuration. Only NEXT_PUBLIC_-prefixed variables may
 * appear in this file — anything else is inlined into the browser bundle.
 * Server-only configuration (if any is ever needed) belongs in a separate
 * module guarded by the `server-only` package, never here.
 */

const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

export const apiBaseUrl: string =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL;
