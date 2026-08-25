/** Client helper for Career Match FastAPI matching. */

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

export class MatchApiError extends Error {
  readonly status: number | null;

  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "MatchApiError";
    this.status = status;
  }
}

const DEFAULT_API_URL = "http://localhost:8000";

/** API origin for the browser. Prefer NEXT_PUBLIC_API_URL at build time. */
export function getApiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");
}

function detailFromBody(body: unknown): string | null {
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
  if (status === 400 || status === 422) {
    return detail ?? "Please check the resume and job description, then try again.";
  }
  if (status >= 500) {
    return "Career Match ran into a problem while analyzing. Please try again in a moment.";
  }
  return detail ?? `Match request failed (${status}).`;
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
  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}/api/v1/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new MatchApiError(
      "Career Match couldn't reach the analysis service. Make sure the backend is running and try again.",
      null,
    );
  }

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    throw new MatchApiError(
      messageForStatus(response.status, detailFromBody(body)),
      response.status,
    );
  }

  if (!isMatchResponse(body)) {
    throw new MatchApiError(
      "Career Match received an unexpected response from the analysis service.",
      response.status,
    );
  }

  return body;
}
