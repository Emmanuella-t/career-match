import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { SignupForm } from "@/components/signup-form";
import { SiteFooter } from "@/components/site-footer";
import { sanitizeReturnPath } from "@/lib/match-draft";

type SignupPageProps = {
  searchParams: Promise<{ redirect_url?: string }>;
};

export default async function SignupPage({ searchParams }: SignupPageProps) {
  const { isAuthenticated } = await auth();
  const params = await searchParams;
  const redirectUrl = sanitizeReturnPath(params.redirect_url, "/dashboard");

  if (isAuthenticated) {
    redirect(redirectUrl);
  }

  return (
    <>
      <main className="flex flex-1 flex-col">
        <Suspense
          fallback={
            <div className="mx-auto w-full max-w-md px-4 py-16 text-sm text-muted-foreground">
              Loading sign-up…
            </div>
          }
        >
          <SignupForm />
        </Suspense>
      </main>
      <SiteFooter />
    </>
  );
}
