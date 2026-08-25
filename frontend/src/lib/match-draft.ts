import type { MatcherName } from "@/lib/api";

/**
 * Temporary client-side draft so resume/JD/matcher survive the auth gate
 * and login/signup redirects. Never put resume text in query strings.
 */

export type MatchDraft = {
  resume: string;
  job: string;
  matcher: MatcherName;
};

const MATCH_DRAFT_KEY = "cm_match_draft";

const MATCHERS: MatcherName[] = ["semantic", "hybrid", "lexical"];

function canUseStorage(): boolean {
  return (
    typeof window !== "undefined" && typeof window.sessionStorage !== "undefined"
  );
}

function isMatcherName(value: unknown): value is MatcherName {
  return typeof value === "string" && MATCHERS.includes(value as MatcherName);
}

export function saveMatchDraft(draft: MatchDraft): void {
  if (!canUseStorage()) return;
  window.sessionStorage.setItem(MATCH_DRAFT_KEY, JSON.stringify(draft));
}

export function loadMatchDraft(): MatchDraft | null {
  if (!canUseStorage()) return null;

  const raw = window.sessionStorage.getItem(MATCH_DRAFT_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as Partial<MatchDraft>;
    if (
      typeof parsed.resume !== "string" ||
      typeof parsed.job !== "string" ||
      !isMatcherName(parsed.matcher)
    ) {
      return null;
    }
    return {
      resume: parsed.resume,
      job: parsed.job,
      matcher: parsed.matcher,
    };
  } catch {
    return null;
  }
}

export function clearMatchDraft(): void {
  if (!canUseStorage()) return;
  window.sessionStorage.removeItem(MATCH_DRAFT_KEY);
}

/** Safe return path after login/signup (same-origin relative paths only). */
export function sanitizeReturnPath(
  value: string | null | undefined,
  fallback = "/match",
): string {
  if (!value || !value.startsWith("/") || value.startsWith("//")) {
    return fallback;
  }
  return value;
}
