import { afterEach, describe, expect, it } from "vitest";

import {
  canGuestAnalyze,
  clearGuestUsageOnAuth,
  getGuestAnalysisCount,
  getOrCreateGuestSessionId,
  getRemainingGuestAnalyses,
  GUEST_ANALYSIS_LIMIT,
  recordSuccessfulGuestAnalysis,
  shouldGateGuestAnalysis,
} from "@/lib/guest-usage";
import {
  clearMatchDraft,
  loadMatchDraft,
  sanitizeReturnPath,
  saveMatchDraft,
} from "@/lib/match-draft";

afterEach(() => {
  window.localStorage.clear();
  window.sessionStorage.clear();
});

describe("guest usage", () => {
  it("creates and persists a guest session id", () => {
    const first = getOrCreateGuestSessionId();
    const second = getOrCreateGuestSessionId();
    expect(first).toBeTruthy();
    expect(second).toBe(first);
  });

  it("starts at zero and allows analyses under the limit", () => {
    expect(getGuestAnalysisCount()).toBe(0);
    expect(canGuestAnalyze()).toBe(true);
    expect(getRemainingGuestAnalyses()).toBe(GUEST_ANALYSIS_LIMIT);
    expect(shouldGateGuestAnalysis(false)).toBe(false);
  });

  it("increments only via recordSuccessfulGuestAnalysis", () => {
    expect(recordSuccessfulGuestAnalysis()).toBe(1);
    expect(getGuestAnalysisCount()).toBe(1);
    expect(canGuestAnalyze()).toBe(true);
    expect(shouldGateGuestAnalysis(false)).toBe(false);

    expect(recordSuccessfulGuestAnalysis()).toBe(2);
    expect(getGuestAnalysisCount()).toBe(2);
    expect(canGuestAnalyze()).toBe(false);
    expect(shouldGateGuestAnalysis(false)).toBe(true);
  });

  it("gates the third attempt for guests but not authenticated users", () => {
    recordSuccessfulGuestAnalysis();
    recordSuccessfulGuestAnalysis();
    expect(shouldGateGuestAnalysis(false)).toBe(true);
    expect(shouldGateGuestAnalysis(true)).toBe(false);
  });

  it("clears guest usage after authentication", () => {
    recordSuccessfulGuestAnalysis();
    recordSuccessfulGuestAnalysis();
    clearGuestUsageOnAuth();
    expect(getGuestAnalysisCount()).toBe(0);
    expect(canGuestAnalyze()).toBe(true);
    expect(window.localStorage.getItem("cm_guest_session_id")).toBeNull();
  });
});

describe("match draft preservation", () => {
  it("saves and restores resume, job, and matcher", () => {
    saveMatchDraft({
      resume: "resume text",
      job: "job text",
      matcher: "hybrid",
    });
    expect(loadMatchDraft()).toEqual({
      resume: "resume text",
      job: "job text",
      matcher: "hybrid",
    });
  });

  it("clears draft storage", () => {
    saveMatchDraft({
      resume: "resume text",
      job: "job text",
      matcher: "semantic",
    });
    clearMatchDraft();
    expect(loadMatchDraft()).toBeNull();
  });

  it("rejects invalid draft payloads", () => {
    window.sessionStorage.setItem(
      "cm_match_draft",
      JSON.stringify({ resume: "x", job: "y", matcher: "nope" }),
    );
    expect(loadMatchDraft()).toBeNull();
  });

  it("sanitizes return paths and blocks open redirects", () => {
    expect(sanitizeReturnPath("/match")).toBe("/match");
    expect(sanitizeReturnPath("/dashboard")).toBe("/dashboard");
    expect(sanitizeReturnPath("//evil.example")).toBe("/match");
    expect(sanitizeReturnPath("https://evil.example")).toBe("/match");
    expect(sanitizeReturnPath(null, "/dashboard")).toBe("/dashboard");
  });
});
