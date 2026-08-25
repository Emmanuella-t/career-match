import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { LoginForm } from "@/components/login-form";
import { SiteFooter } from "@/components/site-footer";
import { sanitizeReturnPath } from "@/lib/match-draft";

type LoginPageProps = {
  searchParams: Promise<{ redirect_url?: string }>;
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
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
              Loading sign-in…
            </div>
          }
        >
          <LoginForm />
        </Suspense>
      </main>
      <SiteFooter />
    </>
  );
}
