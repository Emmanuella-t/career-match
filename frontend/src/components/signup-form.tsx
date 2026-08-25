"use client";

import { SignUp } from "@clerk/nextjs";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { AuthShell } from "@/components/auth-shell";
import { clerkAppearance } from "@/lib/clerk-appearance";
import { sanitizeReturnPath } from "@/lib/match-draft";

export function SignupForm() {
  const searchParams = useSearchParams();
  const redirectUrl = sanitizeReturnPath(
    searchParams.get("redirect_url"),
    "/dashboard",
  );

  return (
    <AuthShell
      title="Create account"
      subtitle="Sign up free to keep matching and open your dashboard."
      footer={
        <>
          Already have an account?{" "}
          <Link
            href={`/login?redirect_url=${encodeURIComponent(redirectUrl)}`}
            className="font-medium text-career-green underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            Log in
          </Link>
          {" · "}
          <Link
            href="/match"
            className="font-medium text-primary underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            Try without an account
          </Link>
        </>
      }
    >
      <SignUp
        routing="hash"
        forceRedirectUrl={redirectUrl}
        fallbackRedirectUrl={redirectUrl}
        signInUrl={`/login?redirect_url=${encodeURIComponent(redirectUrl)}`}
        appearance={clerkAppearance}
      />
    </AuthShell>
  );
}
