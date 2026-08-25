import Link from "next/link";

import { BrandIcon } from "@/components/brand-mark";

const GITHUB_URL = "https://github.com/Emmanuella-t/career-match";

export function LandingFooter() {
  return (
    <footer className="border-t border-primary/10">
      <div className="mx-auto flex w-full max-w-[1240px] flex-col gap-6 px-4 py-10 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="flex items-start gap-3">
          <BrandIcon className="mt-0.5 size-7" />
          <div className="space-y-1">
            <p className="font-sans text-sm font-semibold text-primary">
              Career Match
            </p>
            <p className="font-body max-w-md text-sm leading-relaxed text-muted-foreground">
              Built with machine learning, NLP, and thoughtful product design.
            </p>
          </div>
        </div>

        <nav
          className="flex flex-wrap gap-x-6 gap-y-2 font-sans text-sm text-muted-foreground"
          aria-label="Footer"
        >
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            GitHub
          </a>
          <a
            href="#how-it-works"
            className="hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            How It Works
          </a>
          <Link
            href="/architecture"
            className="hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            Project Documentation
          </Link>
        </nav>
      </div>
    </footer>
  );
}
