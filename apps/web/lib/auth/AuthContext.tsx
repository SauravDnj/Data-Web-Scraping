"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { apiFetch } from "@/lib/api/client";
import { clearStoredToken, readStoredToken, writeStoredToken } from "./storage";

export type CurrentUser = {
  id: number;
  email: string;
  status: string;
};

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

type AuthContextValue = {
  status: AuthStatus;
  user: CurrentUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Wraps the whole app (root layout) so both `/login` and the
 * authenticated shell share one session source of truth. On mount,
 * validates any stored token against `GET /auth/me` rather than
 * trusting its mere presence — an expired or revoked token must not
 * render the shell as if it were still signed in.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  // Lazy initializer, not an effect: whether a token is even present
  // is knowable synchronously at first client render, so starting at
  // "loading" and flipping to "unauthenticated" a tick later via
  // setState-in-effect would just be an avoidable extra render (and
  // trips react-hooks/set-state-in-effect). The one accepted trade-off
  // is a possible hydration mismatch for a returning, already-signed-in
  // visitor, since the server has no access to sessionStorage — the
  // same trade-off every client-storage-backed auth check makes; React
  // resolves it by taking the client's value, not by failing.
  const [status, setStatus] = useState<AuthStatus>(() =>
    readStoredToken() ? "loading" : "unauthenticated",
  );
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = readStoredToken();
    if (!stored) return;

    let cancelled = false;
    apiFetch<CurrentUser>("/auth/me", {
      headers: { Authorization: `Bearer ${stored}` },
    })
      .then((me) => {
        if (cancelled) return;
        setToken(stored);
        setUser(me);
        setStatus("authenticated");
      })
      .catch(() => {
        if (cancelled) return;
        clearStoredToken();
        setStatus("unauthenticated");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const issued = await apiFetch<{ token: string; expires_at: string }>(
      "/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) },
    );
    const me = await apiFetch<CurrentUser>("/auth/me", {
      headers: { Authorization: `Bearer ${issued.token}` },
    });
    writeStoredToken(issued.token);
    setToken(issued.token);
    setUser(me);
    setStatus("authenticated");
  }, []);

  const logout = useCallback(async () => {
    if (token) {
      try {
        await apiFetch<void>("/auth/logout", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch {
        // Best-effort: the token is discarded client-side regardless,
        // so a failed logout call never leaves the user stuck signed in.
      }
    }
    clearStoredToken();
    setToken(null);
    setUser(null);
    setStatus("unauthenticated");
  }, [token]);

  return (
    <AuthContext.Provider value={{ status, user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
