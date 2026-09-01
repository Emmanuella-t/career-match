/** Authenticated persistence API helpers (Clerk token → FastAPI → Postgres). */

import { apiFetch, ApiError, detailFromBody, getApiBaseUrl, type MatchResponse } from "@/lib/api";

export type ResumeRecord = {
  id: string;
  clerk_user_id: string;
  name: string;
  resume_text: string;
  created_at: string;
  updated_at: string;
};

export type MatchAnalysisRecord = {
  id: string;
  clerk_user_id: string;
  resume_id: string | null;
  job_title: string | null;
  company: string | null;
  job_description: string;
  matcher: string;
  matcher_version: string | null;
  overall_score: number;
  matched_skills: string[];
  missing_skills: string[];
  weak_or_negated_skills: string[];
  semantic_score: number | null;
  tfidf_score: number | null;
  skill_overlap_score: number | null;
  disclaimer: string | null;
  created_at: string;
};

export type SavedJobRecord = {
  id: string;
  clerk_user_id: string;
  title: string;
  company: string | null;
  job_description: string;
  source_url: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ResumeCreatePayload = {
  name: string;
  resume_text: string;
};

export type ResumeUpdatePayload = {
  name?: string;
  resume_text?: string;
};

export type SavedJobCreatePayload = {
  title: string;
  company?: string | null;
  job_description: string;
  source_url?: string | null;
  notes?: string | null;
};

export type SavedJobUpdatePayload = {
  title?: string;
  company?: string | null;
  job_description?: string;
  source_url?: string | null;
  notes?: string | null;
};

export type SaveMatchPayload = {
  resume_id?: string | null;
  job_title?: string | null;
  company?: string | null;
  job_description: string;
  matcher: string;
  matcher_version?: string | null;
  overall_score: number;
  matched_skills: string[];
  missing_skills: string[];
  weak_or_negated_skills: string[];
  semantic_score?: number | null;
  tfidf_score?: number | null;
  skill_overlap_score?: number | null;
  disclaimer?: string | null;
};

export type JobOpportunityRecord = {
  id: string;
  title: string;
  company: string | null;
  location: string | null;
  description: string;
  source: string;
  source_url: string | null;
  apply_url: string | null;
  employment_type: string | null;
  created_at: string;
  updated_at: string;
};

export type RankedJobResult = {
  job: JobOpportunityRecord;
  overall_score: number;
  matched_skills: string[];
  missing_skills: string[];
  weak_or_negated_skills: string[];
  matcher: string;
  matcher_version: string;
  semantic_score: number | null;
  tfidf_score: number | null;
  skill_overlap_score: number | null;
  disclaimer: string;
};

export type JobDiscoverPayload = {
  resume_id?: string;
  resume_text?: string;
  limit?: number;
  location?: string;
  employment_type?: string;
  matcher?: "semantic" | "hybrid" | "lexical";
};

export type JobDiscoverResponse = {
  results: RankedJobResult[];
  matcher: string;
  matcher_version: string;
  disclaimer: string;
  resume_id: string | null;
  source: string;
  search_query: string | null;
  candidate_count: number;
  provider_message: string | null;
};

function requireToken(token: string | null | undefined): string {
  if (!token) {
    throw new ApiError("Sign in to use saved resumes and dashboard features.", 401);
  }
  return token;
}

export async function listResumes(token: string | null): Promise<ResumeRecord[]> {
  return apiFetch<ResumeRecord[]>("/api/v1/resumes", {
    token: requireToken(token),
  });
}

export async function createResume(
  token: string | null,
  payload: ResumeCreatePayload,
): Promise<ResumeRecord> {
  return apiFetch<ResumeRecord>("/api/v1/resumes", {
    method: "POST",
    token: requireToken(token),
    body: payload,
  });
}

export async function getResume(
  token: string | null,
  resumeId: string,
): Promise<ResumeRecord> {
  return apiFetch<ResumeRecord>(`/api/v1/resumes/${resumeId}`, {
    token: requireToken(token),
  });
}

export async function updateResume(
  token: string | null,
  resumeId: string,
  payload: ResumeUpdatePayload,
): Promise<ResumeRecord> {
  return apiFetch<ResumeRecord>(`/api/v1/resumes/${resumeId}`, {
    method: "PATCH",
    token: requireToken(token),
    body: payload,
  });
}

export async function deleteResume(
  token: string | null,
  resumeId: string,
): Promise<void> {
  await apiFetch<void>(`/api/v1/resumes/${resumeId}`, {
    method: "DELETE",
    token: requireToken(token),
  });
}

export async function listMatches(
  token: string | null,
): Promise<MatchAnalysisRecord[]> {
  return apiFetch<MatchAnalysisRecord[]>("/api/v1/matches", {
    token: requireToken(token),
  });
}

export async function getMatch(
  token: string | null,
  matchId: string,
): Promise<MatchAnalysisRecord> {
  return apiFetch<MatchAnalysisRecord>(`/api/v1/matches/${matchId}`, {
    token: requireToken(token),
  });
}

export async function saveMatchAnalysis(
  token: string | null,
  payload: SaveMatchPayload,
): Promise<MatchAnalysisRecord> {
  return apiFetch<MatchAnalysisRecord>("/api/v1/matches", {
    method: "POST",
    token: requireToken(token),
    body: payload,
  });
}

export async function deleteMatch(
  token: string | null,
  matchId: string,
): Promise<void> {
  await apiFetch<void>(`/api/v1/matches/${matchId}`, {
    method: "DELETE",
    token: requireToken(token),
  });
}

export async function listJobs(token: string | null): Promise<SavedJobRecord[]> {
  return apiFetch<SavedJobRecord[]>("/api/v1/jobs", {
    token: requireToken(token),
  });
}

export async function createJob(
  token: string | null,
  payload: SavedJobCreatePayload,
): Promise<SavedJobRecord> {
  return apiFetch<SavedJobRecord>("/api/v1/jobs", {
    method: "POST",
    token: requireToken(token),
    body: payload,
  });
}

export async function getJob(
  token: string | null,
  jobId: string,
): Promise<SavedJobRecord> {
  return apiFetch<SavedJobRecord>(`/api/v1/jobs/${jobId}`, {
    token: requireToken(token),
  });
}

export async function updateJob(
  token: string | null,
  jobId: string,
  payload: SavedJobUpdatePayload,
): Promise<SavedJobRecord> {
  return apiFetch<SavedJobRecord>(`/api/v1/jobs/${jobId}`, {
    method: "PATCH",
    token: requireToken(token),
    body: payload,
  });
}

export async function deleteJob(
  token: string | null,
  jobId: string,
): Promise<void> {
  await apiFetch<void>(`/api/v1/jobs/${jobId}`, {
    method: "DELETE",
    token: requireToken(token),
  });
}

export async function discoverJobs(
  token: string | null,
  payload: JobDiscoverPayload,
): Promise<JobDiscoverResponse> {
  return apiFetch<JobDiscoverResponse>("/api/v1/jobs/discover", {
    method: "POST",
    token: requireToken(token),
    body: payload,
  });
}

export type TailorTarget = "summary" | "experience" | "projects" | "skills" | "all";

export type EvidenceMapEntry = {
  requirement: string;
  status: string;
  supporting_text: string | null;
  support_reason: string;
  confidence: string;
};

export type RewriteSuggestionRecord = {
  suggestion_id: string;
  section: string;
  original_text: string;
  suggested_text: string;
  keywords_introduced: string[];
  support_reason: string;
  support_level: string;
};

export type ResumeTailorPayload = {
  resume_id?: string;
  resume_text?: string;
  job_id?: string;
  job_description?: string;
  target?: TailorTarget;
  matcher?: "semantic" | "hybrid" | "lexical";
};

export type ResumeTailorResponse = {
  original_alignment_score: number;
  matcher: string;
  matcher_version: string;
  semantic_score: number | null;
  tfidf_score: number | null;
  skill_overlap_score: number | null;
  supported_keywords: string[];
  unsupported_keywords: string[];
  missing_requirements: string[];
  evidence_map: EvidenceMapEntry[];
  rewrite_suggestions: RewriteSuggestionRecord[];
  warnings: string[];
  disclaimer: string;
  resume_id: string | null;
  job_id: string | null;
  rewrite_generation_available: boolean;
  llm_rewrite_available: boolean;
};

export async function tailorResume(
  token: string | null,
  payload: ResumeTailorPayload,
): Promise<ResumeTailorResponse> {
  return apiFetch<ResumeTailorResponse>("/api/v1/resumes/tailor", {
    method: "POST",
    token: requireToken(token),
    body: payload,
  });
}

export type ResumeTailorApplyPayload = ResumeTailorPayload & {
  accepted_suggestion_ids: string[];
};

export type RevisedSectionBlock = {
  section: string;
  text: string;
  change_status: string;
  original_text: string | null;
  suggestion_id: string | null;
};

export type ResumeTailorApplyResponse = {
  structured_sections: RevisedSectionBlock[];
  revised_resume_text: string;
  original_alignment_score: number;
  revised_alignment_score: number;
  alignment_delta: number;
  newly_covered_keywords: string[];
  remaining_missing_requirements: string[];
  remaining_unsupported_keywords: string[];
  accepted_suggestions: RewriteSuggestionRecord[];
  rejected_suggestions: RewriteSuggestionRecord[];
  warnings: string[];
  disclaimer: string;
  matcher: string;
  matcher_version: string;
  resume_id: string | null;
  job_id: string | null;
};

export async function applyTailorRevision(
  token: string | null,
  payload: ResumeTailorApplyPayload,
): Promise<ResumeTailorApplyResponse> {
  return apiFetch<ResumeTailorApplyResponse>("/api/v1/resumes/tailor/apply", {
    method: "POST",
    token: requireToken(token),
    body: payload,
  });
}

export type ResumeExportPayload = ResumeTailorApplyPayload & {
  format: "docx" | "txt";
};

function filenameFromDisposition(header: string | null): string | null {
  if (!header) return null;
  const match = /filename="([^"]+)"/i.exec(header);
  return match?.[1] ?? null;
}

export async function exportTailoredResume(
  token: string | null,
  payload: ResumeExportPayload,
): Promise<{ blob: Blob; filename: string }> {
  const authToken = requireToken(token);
  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}/api/v1/resumes/export`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ApiError(
      "Career Match couldn't reach the export service. Make sure the backend is running and try again.",
      null,
    );
  }

  if (!response.ok) {
    let parsed: unknown = null;
    try {
      parsed = await response.json();
    } catch {
      parsed = null;
    }
    throw new ApiError(
      detailFromBody(parsed) ?? "Could not export tailored resume.",
      response.status,
    );
  }

  const blob = await response.blob();
  const fallback =
    payload.format === "docx" ? "resume_tailored.docx" : "resume_tailored.txt";
  const filename =
    filenameFromDisposition(response.headers.get("Content-Disposition")) ??
    fallback;
  return { blob, filename };
}

/** Build a save payload from a live match response + job context. */
export function buildSaveMatchPayload(args: {
  result: MatchResponse;
  jobDescription: string;
  jobTitle?: string;
  company?: string;
  resumeId?: string | null;
}): SaveMatchPayload {
  const { result, jobDescription, jobTitle, company, resumeId } = args;
  return {
    resume_id: resumeId ?? null,
    job_title: jobTitle?.trim() || null,
    company: company?.trim() || null,
    job_description: jobDescription,
    matcher: result.matcher,
    matcher_version: result.matcher_version,
    overall_score: result.overall_score,
    matched_skills: result.matched_skills,
    missing_skills: result.missing_skills,
    weak_or_negated_skills: result.weak_or_negated_skills,
    semantic_score: result.semantic_score,
    tfidf_score: result.tfidf_score,
    skill_overlap_score: result.skill_overlap_score,
    disclaimer: result.disclaimer,
  };
}
