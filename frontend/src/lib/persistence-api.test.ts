import { afterEach, describe, expect, it, vi } from "vitest";

import { buildSaveMatchPayload } from "@/lib/persistence-api";
import type { MatchResponse } from "@/lib/api";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("buildSaveMatchPayload", () => {
  it("maps a match response without inventing scores", () => {
    const result: MatchResponse = {
      matcher: "Semantic Matcher v0.1",
      matcher_version: "0.1.0",
      overall_score: 72,
      semantic_score: 0.71,
      tfidf_score: null,
      skill_overlap_score: null,
      matched_skills: ["python"],
      missing_skills: ["docker"],
      weak_or_negated_skills: [],
      disclaimer: "not a hiring probability",
    };

    expect(
      buildSaveMatchPayload({
        result,
        jobDescription: "Need Python.",
        jobTitle: "Engineer",
        company: "Acme",
        resumeId: "res-1",
      }),
    ).toEqual({
      resume_id: "res-1",
      job_title: "Engineer",
      company: "Acme",
      job_description: "Need Python.",
      matcher: "Semantic Matcher v0.1",
      matcher_version: "0.1.0",
      overall_score: 72,
      matched_skills: ["python"],
      missing_skills: ["docker"],
      weak_or_negated_skills: [],
      semantic_score: 0.71,
      tfidf_score: null,
      skill_overlap_score: null,
      disclaimer: "not a hiring probability",
    });
  });
});
