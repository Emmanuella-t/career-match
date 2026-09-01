import { describe, expect, it } from "vitest";

import {
  loadTailorContext,
  saveTailorContext,
  clearTailorContext,
} from "@/lib/tailor-context";

describe("tailor context", () => {
  it("round-trips resume text without a saved resume id", () => {
    clearTailorContext();
    saveTailorContext({
      resumeText: "Jordan Lee\nPython engineer",
      jobDescription: "Need Python and Docker.",
      jobTitle: "Backend role",
    });
    const loaded = loadTailorContext();
    expect(loaded?.resumeText).toContain("Jordan Lee");
    expect(loaded?.resumeId).toBeUndefined();
    expect(loaded?.jobDescription).toContain("Python");
    expect(loaded?.jobTitle).toBe("Backend role");
    clearTailorContext();
  });
});
