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

const DEFAULT_API_URL = "http://localhost:8000";

export function getApiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");
}

export async function matchResumeToJob(
  payload: MatchRequest,
): Promise<MatchResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail = `Match request failed (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      // keep status-based message
    }
    throw new Error(detail);
  }

  return (await response.json()) as MatchResponse;
}
