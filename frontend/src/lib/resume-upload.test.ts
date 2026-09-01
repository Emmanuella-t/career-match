import { describe, expect, it } from "vitest";

import { ApiError } from "@/lib/api";
import {
  isAllowedResumeFile,
  mapResumeUploadError,
  MAX_RESUME_FILE_BYTES,
  validateResumeFileSelection,
} from "@/lib/resume-upload";

describe("validateResumeFileSelection", () => {
  it("rejects unsupported file types", () => {
    const file = new File(["hello"], "resume.txt", { type: "text/plain" });
    expect(validateResumeFileSelection(file)).toBe("Upload a PDF or DOCX resume.");
  });

  it("accepts pdf and docx files within size limits", () => {
    const pdf = new File(["%PDF"], "resume.pdf", { type: "application/pdf" });
    const docx = new File(["docx"], "resume.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    expect(validateResumeFileSelection(pdf)).toBeNull();
    expect(validateResumeFileSelection(docx)).toBeNull();
  });

  it("rejects oversized files", () => {
    const file = new File([new Uint8Array(MAX_RESUME_FILE_BYTES + 1)], "big.pdf", {
      type: "application/pdf",
    });
    expect(validateResumeFileSelection(file)).toContain("too large");
  });
});

describe("isAllowedResumeFile", () => {
  it("allows pdf and docx extensions", () => {
    expect(isAllowedResumeFile(new File([], "resume.PDF"))).toBe(true);
    expect(isAllowedResumeFile(new File([], "resume.docx"))).toBe(true);
    expect(isAllowedResumeFile(new File([], "resume.txt"))).toBe(false);
  });
});

describe("mapResumeUploadError", () => {
  it("maps unsupported file errors", () => {
    expect(
      mapResumeUploadError(
        new ApiError("unsupported file type; supported formats are PDF and DOCX", 400),
      ),
    ).toBe("Upload a PDF or DOCX resume.");
  });

  it("maps scanned pdf errors", () => {
    expect(
      mapResumeUploadError(
        new ApiError(
          "no extractable text was found in this PDF. Scanned or image-only PDFs are not supported yet",
          400,
        ),
      ),
    ).toBe("We couldn't read text from this PDF. Try a text-based PDF or DOCX file.");
  });

  it("maps generic parse failures", () => {
    expect(mapResumeUploadError(new ApiError("could not read PDF file", 400))).toBe(
      "We couldn't read that resume. Try another file.",
    );
    expect(mapResumeUploadError(new Error("network"))).toBe(
      "We couldn't read that resume. Try another file.",
    );
  });
});
