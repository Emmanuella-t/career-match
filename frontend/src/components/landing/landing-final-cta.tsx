import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function LandingFinalCta() {
  return (
    <section
      id="cta"
      className="mx-auto w-full max-w-[1240px] px-4 py-16 sm:px-6 sm:py-20 lg:px-8"
      aria-labelledby="final-cta-heading"
    >
      <div className="rounded-[2rem] bg-primary px-7 py-10 text-primary-foreground shadow-[0_18px_40px_rgba(23,63,53,0.16)] sm:px-10 sm:py-12 lg:flex lg:items-center lg:justify-between lg:gap-10">
        <div className="max-w-2xl space-y-3">
          <h2
            id="final-cta-heading"
            className="font-headline text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl"
          >
            Your next opportunity should be a better match.
          </h2>
          <p className="font-body text-base leading-relaxed text-primary-foreground/85 sm:text-lg">
            Upload your resume and discover how well your experience aligns with
            the roles you want.
          </p>
        </div>
        <Link
          href="/match"
          className={cn(
            buttonVariants({ size: "lg" }),
            "font-cta mt-6 inline-flex h-12 shrink-0 bg-career-green px-6 text-base text-primary hover:bg-career-green/90 lg:mt-0",
          )}
        >
          Try Career Match →
        </Link>
      </div>
    </section>
  );
}
