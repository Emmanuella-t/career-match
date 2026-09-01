import { describe, expect, it } from "vitest";

import {
  buildDiscoverPayload,
  isDiscoverCtaEnabled,
  onResumeSourceModeChange,
  resolveActiveResumeText,
} from "@/lib/discovery-resume";

describe("buildDiscoverPayload", () => {
  it("uses resume_id for saved resume discovery", () => {
    expect(
      buildDiscoverPayload("saved", {
        selectedResumeId: "res-1",
        uploadedResumeText: null,
        location: " Remote ",
        employmentType: " full-time ",
      }),
    ).toEqual({
      resume_id: "res-1",
      location: "Remote",
      employment_type: "full-time",
    });
  });

  it("uses resume_text for direct upload discovery", () => {
    expect(
      buildDiscoverPayload("upload", {
        selectedResumeId: "",
        uploadedResumeText: " Jordan Lee\nPython engineer ",
        location: "Austin",
      }),
    ).toEqual({
      resume_text: "Jordan Lee\nPython engineer",
      location: "Austin",
    });
  });

  it("never mixes resume_id and resume_text", () => {
    const saved = buildDiscoverPayload("saved", {
      selectedResumeId: "res-1",
      uploadedResumeText: "uploaded text",
    });
    const uploaded = buildDiscoverPayload("upload", {
      selectedResumeId: "res-1",
      uploadedResumeText: "uploaded text",
    });

    expect(saved).toEqual({ resume_id: "res-1" });
    expect(saved).not.toHaveProperty("resume_text");
    expect(uploaded).toEqual({ resume_text: "uploaded text" });
    expect(uploaded).not.toHaveProperty("resume_id");
  });

  it("returns null when no resume is ready", () => {
    expect(
      buildDiscoverPayload("saved", {
        selectedResumeId: "",
        uploadedResumeText: null,
      }),
    ).toBeNull();
    expect(
      buildDiscoverPayload("upload", {
        selectedResumeId: "",
        uploadedResumeText: null,
      }),
    ).toBeNull();
  });
});

describe("isDiscoverCtaEnabled", () => {
  it("requires a selected saved resume", () => {
    expect(isDiscoverCtaEnabled("saved", "res-1", null, "idle")).toBe(true);
    expect(isDiscoverCtaEnabled("saved", "", null, "idle")).toBe(false);
  });

  it("requires a ready uploaded resume", () => {
    expect(isDiscoverCtaEnabled("upload", "", "Python engineer", "ready")).toBe(true);
    expect(isDiscoverCtaEnabled("upload", "", "Python engineer", "reading")).toBe(false);
    expect(isDiscoverCtaEnabled("upload", "", null, "ready")).toBe(false);
  });
});

describe("onResumeSourceModeChange", () => {
  it("clears upload state when switching to saved resume", () => {
    expect(onResumeSourceModeChange("saved")).toEqual({
      clearSavedSelection: false,
      clearUpload: true,
    });
  });

  it("clears saved selection when switching to upload", () => {
    expect(onResumeSourceModeChange("upload")).toEqual({
      clearSavedSelection: true,
      clearUpload: false,
    });
  });
});

describe("resolveActiveResumeText", () => {
  const resumes = [
    { id: "res-1", resume_text: "Saved resume text" },
    { id: "res-2", resume_text: "Other resume" },
  ];

  it("returns saved resume text in saved mode", () => {
    expect(resolveActiveResumeText("saved", resumes, "res-1", null)).toBe(
      "Saved resume text",
    );
  });

  it("returns uploaded text in upload mode", () => {
    expect(resolveActiveResumeText("upload", resumes, "res-1", "Uploaded text")).toBe(
      "Uploaded text",
    );
  });
});
