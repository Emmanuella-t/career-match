export type TailorContext = {
  resumeId?: string;
  jobDescription: string;
  jobTitle?: string;
};

const TAILOR_CONTEXT_KEY = "cm_tailor_context";

function canUseStorage(): boolean {
  return (
    typeof window !== "undefined" && typeof window.sessionStorage !== "undefined"
  );
}

export function saveTailorContext(context: TailorContext): void {
  if (!canUseStorage()) return;
  window.sessionStorage.setItem(TAILOR_CONTEXT_KEY, JSON.stringify(context));
}

export function loadTailorContext(): TailorContext | null {
  if (!canUseStorage()) return null;
  const raw = window.sessionStorage.getItem(TAILOR_CONTEXT_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<TailorContext>;
    if (typeof parsed.jobDescription !== "string" || !parsed.jobDescription.trim()) {
      return null;
    }
    return {
      resumeId: parsed.resumeId,
      jobDescription: parsed.jobDescription,
      jobTitle: parsed.jobTitle,
    };
  } catch {
    return null;
  }
}

export function clearTailorContext(): void {
  if (!canUseStorage()) return;
  window.sessionStorage.removeItem(TAILOR_CONTEXT_KEY);
}
