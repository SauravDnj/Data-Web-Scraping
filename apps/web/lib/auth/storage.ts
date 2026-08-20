"use client";

/**
 * Where the session token lives, and the trade-off that decision makes
 * (T070, no dedicated login/session task exists anywhere in the
 * documented task list — see docs/16_MEMORY.md for the fuller
 * reasoning):
 *
 * The backend (T038) issues a bearer token, not a cookie
 * (`app/api/v1/auth.py`'s `LoginResponse.token`), and already
 * configures CORS for a configured `frontend_origin`
 * (`apps/api/app/main.py`) — the architecture this app was already
 * set up for is the browser calling the API directly, not a Next.js
 * server-side proxy. `sessionStorage` is the token store: it survives
 * a page refresh (unlike an in-memory-only store, which would force a
 * re-login on every reload) but clears when the tab closes (unlike
 * `localStorage`, which would persist indefinitely). It is still
 * readable by any script on the page, same as every `sessionStorage`-
 * based token store — an XSS vulnerability elsewhere in the app could
 * exfiltrate it. Revisiting this for an httpOnly-cookie/BFF proxy
 * design is a reasonable future hardening step (candidate for T090,
 * Security review) but is out of scope for the shell itself.
 */

const SESSION_TOKEN_KEY = "gmdp.session_token";

export function readStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.sessionStorage.getItem(SESSION_TOKEN_KEY);
}

export function writeStoredToken(token: string): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(SESSION_TOKEN_KEY, token);
}

export function clearStoredToken(): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.removeItem(SESSION_TOKEN_KEY);
}
