import type { JobDiscoverPayload } from "@/lib/persistence-api";

export type ResumeSourceMode = "saved" | "upload";

export type UploadStatus = "idle" | "uploading" | "reading" | "ready" | "error";

export function isDiscoverCtaEnabled(
  mode: ResumeSourceMode,
  selectedResumeId: string,
  uploadedResumeText: string | null,
  uploadStatus: UploadStatus,
): boolean {
  if (mode === "saved") {
    return Boolean(selectedResumeId);
  }
  return uploadStatus === "ready" && Boolean(uploadedResumeText?.trim());
}

export function buildDiscoverPayload(
  mode: ResumeSourceMode,
  options: {
    selectedResumeId: string;
    uploadedResumeText: string | null;
    location?: string;
    employmentType?: string;
  },
): JobDiscoverPayload | null {
  const location = options.location?.trim() || undefined;
  const employment_type = options.employmentType?.trim() || undefined;

  if (mode === "saved") {
    if (!options.selectedResumeId) {
      return null;
    }
    return {
      resume_id: options.selectedResumeId,
      location,
      employment_type,
    };
  }

  const resumeText = options.uploadedResumeText?.trim();
  if (!resumeText) {
    return null;
  }
  return {
    resume_text: resumeText,
    location,
    employment_type,
  };
}

/** Clear conflicting resume source when switching tabs. */
export function onResumeSourceModeChange(
  nextMode: ResumeSourceMode,
): {
  clearSavedSelection: boolean;
  clearUpload: boolean;
} {
  if (nextMode === "saved") {
    return { clearSavedSelection: false, clearUpload: true };
  }
  return { clearSavedSelection: true, clearUpload: false };
}

export function resolveActiveResumeText(
  mode: ResumeSourceMode,
  resumes: Array<{ id: string; resume_text: string }>,
  selectedResumeId: string,
  uploadedResumeText: string | null,
): string | null {
  if (mode === "saved") {
    const resume = resumes.find((row) => row.id === selectedResumeId);
    return resume?.resume_text ?? null;
  }
  return uploadedResumeText?.trim() || null;
}
