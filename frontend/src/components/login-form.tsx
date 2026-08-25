"use client";

import { SignIn } from "@clerk/nextjs";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { AuthShell } from "@/components/auth-shell";
import { clerkAppearance } from "@/lib/clerk-appearance";
import { sanitizeReturnPath } from "@/lib/match-draft";

export function LoginForm() {
  const searchParams = useSearchParams();
  const redirectUrl = sanitizeReturnPath(
    searchParams.get("redirect_url"),
    "/dashboard",
  );

  return (
    <AuthShell
      title="Log in"
      subtitle="Welcome back. Continue matching with your Career Match account."
      footer={
        <>
          New here?{" "}
          <Link
            href={`/signup?redirect_url=${encodeURIComponent(redirectUrl)}`}
            className="font-medium text-career-green underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            Create an account
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
      <SignIn
        routing="hash"
        forceRedirectUrl={redirectUrl}
        fallbackRedirectUrl={redirectUrl}
        signUpUrl={`/signup?redirect_url=${encodeURIComponent(redirectUrl)}`}
        appearance={clerkAppearance}
      />
    </AuthShell>
  );
}
