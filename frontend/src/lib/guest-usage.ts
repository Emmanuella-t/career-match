/**
 * Client-side guest analysis usage tracking.
 *
 * This is a product-flow aid for the guest milestone, not tamper-proof
 * enforcement. Production public limits should be server-backed.
 */

export const GUEST_ANALYSIS_LIMIT = 2;

const GUEST_SESSION_ID_KEY = "cm_guest_session_id";
const GUEST_ANALYSIS_COUNT_KEY = "cm_guest_analysis_count";

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function createGuestSessionId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `guest_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

/** Returns the persisted guest session id, creating one when missing. */
export function getOrCreateGuestSessionId(): string {
  if (!canUseStorage()) return createGuestSessionId();

  const existing = window.localStorage.getItem(GUEST_SESSION_ID_KEY);
  if (existing && existing.trim()) return existing;

  const id = createGuestSessionId();
  window.localStorage.setItem(GUEST_SESSION_ID_KEY, id);
  return id;
}

/** Successful guest analyses completed in this browser session identity. */
export function getGuestAnalysisCount(): number {
  if (!canUseStorage()) return 0;

  const raw = window.localStorage.getItem(GUEST_ANALYSIS_COUNT_KEY);
  const parsed = raw == null ? 0 : Number.parseInt(raw, 10);
  if (!Number.isFinite(parsed) || parsed < 0) return 0;
  return parsed;
}

/** Whether a guest may start another analysis (limit is exclusive of the next). */
export function canGuestAnalyze(count: number = getGuestAnalysisCount()): boolean {
  return count < GUEST_ANALYSIS_LIMIT;
}

/**
 * True when an unauthenticated user has already used their free analyses
 * and the next attempt should show the auth gate.
 */
export function shouldGateGuestAnalysis(isAuthenticated: boolean): boolean {
  if (isAuthenticated) return false;
  return !canGuestAnalyze();
}

/**
 * Increment only after a successful analysis response.
 * Ensures a guest session id exists first.
 */
export function recordSuccessfulGuestAnalysis(): number {
  getOrCreateGuestSessionId();
  const next = getGuestAnalysisCount() + 1;
  if (canUseStorage()) {
    window.localStorage.setItem(GUEST_ANALYSIS_COUNT_KEY, String(next));
  }
  return next;
}

/**
 * Clear guest usage after the user authenticates so signed-in sessions
 * are not constrained by prior guest counts in this browser.
 */
export function clearGuestUsageOnAuth(): void {
  if (!canUseStorage()) return;
  window.localStorage.removeItem(GUEST_ANALYSIS_COUNT_KEY);
  window.localStorage.removeItem(GUEST_SESSION_ID_KEY);
}

/** Remaining free guest analyses (never negative). */
export function getRemainingGuestAnalyses(
  count: number = getGuestAnalysisCount(),
): number {
  return Math.max(0, GUEST_ANALYSIS_LIMIT - count);
}
