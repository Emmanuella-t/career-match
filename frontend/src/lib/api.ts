/** Shared FastAPI client helpers (public match + authenticated persistence). */

export type MatcherName = "semantic" | "hybrid" | "lexical";

export type MatchRequest = {
  resume_text: string;
  job_description: string;
  matcher?: MatcherName;
};

export type MatchResponse = {
  matcher: string;
  matcher_version: string;
  overall_score: number;
  semantic_score: number | null;
  tfidf_score: number | null;
  skill_overlap_score: number | null;
  matched_skills: string[];
  missing_skills: string[];
  weak_or_negated_skills: string[];
  disclaimer: string;
};

export class ApiError extends Error {
  readonly status: number | null;

  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** @deprecated Prefer ApiError; kept for existing match-form catch sites. */
export class MatchApiError extends ApiError {
  constructor(message: string, status: number | null = null) {
    super(message, status);
    this.name = "MatchApiError";
  }
}

const DEFAULT_API_URL = "http://localhost:8000";

/** API origin for the browser. Prefer NEXT_PUBLIC_API_URL at build time. */
export function getApiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");
}

export function detailFromBody(body: unknown): string | null {
  if (!body || typeof body !== "object") return null;
  const detail = (body as { detail?: unknown }).detail;
  if (typeof detail === "string" && detail.trim()) return detail.trim();
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: unknown }).msg);
        }
        return null;
      })
      .filter((part): part is string => Boolean(part));
    if (parts.length) return parts.join("; ");
  }
  return null;
}

function messageForStatus(status: number, detail: string | null): string {
  if (status === 401) {
    return detail ?? "Please log in again to continue.";
  }
  if (status === 403) {
    return detail ?? "You do not have access to that resource.";
  }
  if (status === 404) {
    return detail ?? "That item was not found.";
  }
  if (status === 400 || status === 422) {
    return detail ?? "Please check your input and try again.";
  }
  if (status === 503) {
    return (
      detail ??
      "Saved data is temporarily unavailable. You can keep matching; try saving again shortly."
    );
  }
  if (status >= 500) {
    return "Career Match ran into a problem. Please try again in a moment.";
  }
  return detail ?? `Request failed (${status}).`;
}

type ApiFetchOptions = {
  method?: string;
  body?: unknown;
  token?: string | null;
  errorName?: "ApiError" | "MatchApiError";
};

export async function apiFetch<T>(
  path: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  const { method = "GET", body, token, errorName = "ApiError" } = options;
  const headers: Record<string, string> = {};
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    const ErrorCtor = errorName === "MatchApiError" ? MatchApiError : ApiError;
    throw new ErrorCtor(
      "Career Match couldn't reach the analysis service. Make sure the backend is running and try again.",
      null,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  let parsed: unknown = null;
  try {
    parsed = await response.json();
  } catch {
    parsed = null;
  }

  if (!response.ok) {
    const ErrorCtor = errorName === "MatchApiError" ? MatchApiError : ApiError;
    throw new ErrorCtor(
      messageForStatus(response.status, detailFromBody(parsed)),
      response.status,
    );
  }

  return parsed as T;
}

function isMatchResponse(value: unknown): value is MatchResponse {
  if (!value || typeof value !== "object") return false;
  const body = value as Record<string, unknown>;
  return (
    typeof body.matcher === "string" &&
    typeof body.matcher_version === "string" &&
    typeof body.overall_score === "number" &&
    Array.isArray(body.matched_skills) &&
    Array.isArray(body.missing_skills) &&
    Array.isArray(body.weak_or_negated_skills) &&
    typeof body.disclaimer === "string"
  );
}

export async function matchResumeToJob(
  payload: MatchRequest,
): Promise<MatchResponse> {
  const body = await apiFetch<unknown>("/api/v1/match", {
    method: "POST",
    body: payload,
    errorName: "MatchApiError",
  });

  if (!isMatchResponse(body)) {
    throw new MatchApiError(
      "Career Match received an unexpected response from the analysis service.",
      200,
    );
  }

  return body;
}
