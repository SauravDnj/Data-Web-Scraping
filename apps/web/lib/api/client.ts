import { apiBaseUrl } from "./config";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly requestId?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type ApiEnvelope<T> = { data: T; request_id: string };
type ApiErrorEnvelope = { error: { message: string }; request_id: string };

/**
 * Minimal typed wrapper around the backend API. No endpoints are called
 * from anywhere yet — this establishes the client/server boundary for
 * later UI tasks (T070+) to build on.
 */
export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  const body = (await response.json()) as ApiEnvelope<T> | ApiErrorEnvelope;

  if (!response.ok || "error" in body) {
    const errorBody = body as ApiErrorEnvelope;
    throw new ApiError(
      errorBody.error?.message ?? "Request failed",
      response.status,
      errorBody.request_id,
    );
  }

  return (body as ApiEnvelope<T>).data;
}
