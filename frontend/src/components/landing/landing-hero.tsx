import Image from "next/image";
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function LandingHero() {
  return (
    <section className="mx-auto w-full max-w-[1240px] px-4 pb-10 pt-8 sm:px-6 sm:pb-14 sm:pt-12 lg:px-8">
      <div className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:gap-12">
        <div className="max-w-xl space-y-6">
          <p className="inline-flex items-center rounded-full border border-career-green/25 bg-mint/20 px-3.5 py-2 font-sans text-xs font-semibold tracking-wide text-primary sm:text-sm">
            AI-powered career matching
          </p>

          <h1 className="font-headline text-[clamp(2.75rem,7vw,5.75rem)] leading-[0.92] font-bold tracking-[-0.03em]">
            <span className="block text-primary">SMARTER MATCHES</span>
            <span className="mt-1 block text-career-green">STRONGER FUTURES</span>
          </h1>

          <p className="font-body max-w-lg text-lg leading-relaxed text-muted-foreground sm:text-xl">
            Career Match analyzes your resume against job opportunities to show
            where you fit, why you fit, and what you can improve.
          </p>

          <div className="space-y-2">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
              <Link
                href="/match"
                className={cn(
                  buttonVariants({ size: "lg" }),
                  "font-cta h-12 bg-primary px-6 text-base text-primary-foreground hover:bg-primary/90",
                )}
              >
                Try Career Match →
              </Link>
              <a
                href="#how-it-works"
                className="font-cta-secondary text-base font-semibold text-career-green underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                See How It Works
              </a>
            </div>
            <p className="font-body text-sm text-muted-foreground">
              No account required to get started.
            </p>
          </div>
        </div>

        <div className="relative mx-auto flex w-full max-w-md items-center justify-center lg:max-w-none">
          <Image
            src="/landing/hero-robot.png"
            alt="Career Match robot holding a resume profile card"
            width={1120}
            height={1280}
            priority
            className="h-auto w-full max-w-[28rem] object-contain sm:max-w-[32rem] lg:max-w-[36rem]"
            sizes="(max-width: 1024px) 90vw, 36rem"
          />
        </div>
      </div>
    </section>
  );
}
