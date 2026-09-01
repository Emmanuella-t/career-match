import { ApiError } from "@/lib/api";

export const RESUME_UPLOAD_ACCEPT =
  ".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document";

/** Matches backend in-memory resume upload cap (2 MiB). */
export const MAX_RESUME_FILE_BYTES = 2 * 1024 * 1024;

export function isAllowedResumeFile(file: File): boolean {
  const lowered = file.name.toLowerCase();
  return lowered.endsWith(".pdf") || lowered.endsWith(".docx");
}

export function validateResumeFileSelection(file: File): string | null {
  if (!isAllowedResumeFile(file)) {
    return "Upload a PDF or DOCX resume.";
  }
  if (file.size > MAX_RESUME_FILE_BYTES) {
    return "That file is too large. Upload a resume up to 2 MB.";
  }
  if (file.size === 0) {
    return "We couldn't read that resume. Try another file.";
  }
  return null;
}

/** Map parse/upload failures to plain-language copy for the UI. */
export function mapResumeUploadError(error: unknown): string {
  if (error instanceof ApiError) {
    const detail = error.message.toLowerCase();
    if (detail.includes("unsupported file type")) {
      return "Upload a PDF or DOCX resume.";
    }
    if (
      detail.includes("scanned") ||
      detail.includes("image-only") ||
      detail.includes("no extractable text")
    ) {
      return "We couldn't read text from this PDF. Try a text-based PDF or DOCX file.";
    }
    if (
      detail.includes("could not read") ||
      detail.includes("empty") ||
      detail.includes("valid pdf") ||
      detail.includes("valid docx")
    ) {
      return "We couldn't read that resume. Try another file.";
    }
    if (detail.includes("exceeds the maximum")) {
      return "That file is too large. Upload a resume up to 2 MB.";
    }
    if (error.status === 401) {
      return "Please sign in to upload a resume file.";
    }
  }
  return "We couldn't read that resume. Try another file.";
}
