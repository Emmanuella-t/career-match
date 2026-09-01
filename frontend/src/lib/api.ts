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

const DEFAULT_API_URL = "http://127.0.0.1:8000";

/** API origin for the browser. Prefer NEXT_PUBLIC_API_URL at build time. */
export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  return (configured || DEFAULT_API_URL).replace(/\/$/, "");
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
      "We're having trouble loading your saved data right now. Please try again."
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
  formData?: FormData;
};

export async function apiFetch<T>(
  path: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  const {
    method = "GET",
    body,
    token,
    errorName = "ApiError",
    formData,
  } = options;
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
      body:
        formData !== undefined
          ? formData
          : body === undefined
            ? undefined
            : JSON.stringify(body),
    });
  } catch {
    const ErrorCtor = errorName === "MatchApiError" ? MatchApiError : ApiError;
    throw new ErrorCtor(
      "We're having trouble connecting right now. Please try again.",
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

export type ResumeParseResponse = {
  filename: string;
  file_type: string;
  character_count: number;
  extracted_text: string;
};

function isResumeParseResponse(value: unknown): value is ResumeParseResponse {
  if (!value || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return (
    typeof record.filename === "string" &&
    typeof record.file_type === "string" &&
    typeof record.character_count === "number" &&
    typeof record.extracted_text === "string"
  );
}

export async function parseResumeFile(
  token: string | null,
  file: File,
): Promise<ResumeParseResponse> {
  if (!token) {
    throw new ApiError("Please log in to upload a resume file.", 401);
  }

  const formData = new FormData();
  formData.append("file", file);

  const body = await apiFetch<unknown>("/api/v1/resumes/parse", {
    method: "POST",
    token,
    formData,
  });

  if (!isResumeParseResponse(body)) {
    throw new ApiError(
      "Career Match received an unexpected response while parsing your resume.",
      200,
    );
  }

  return body;
}
