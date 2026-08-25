/**
 * Auth provider notes (Clerk).
 *
 * Chosen because Career Match already uses Next.js App Router and needs
 * email/password signup, persistent sessions, protected routes, logout,
 * and a path to future dashboard data — without building a password store
 * or session backend in this monorepo. Clerk is a single provider with a
 * maintained Next.js SDK; Auth.js and Supabase would add more wiring for
 * the same milestone surface.
 */

export function isClerkPublishableKeyConfigured(): boolean {
  const key = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  return Boolean(key && key.trim() && !key.includes("placeholder"));
}
