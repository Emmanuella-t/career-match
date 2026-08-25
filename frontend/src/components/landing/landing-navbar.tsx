import Link from "next/link";

import { BrandLogoCompact } from "@/components/brand-mark";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const GITHUB_URL = "https://github.com/Emmanuella-t/career-match";

const links = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How It Works" },
  { href: "#about", label: "About" },
  { href: GITHUB_URL, label: "GitHub", external: true },
];

export function LandingNavbar() {
  return (
    <header className="border-b border-primary/10 bg-background/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-[1240px] flex-col gap-4 px-4 py-5 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/"
            className="inline-flex shrink-0 rounded-sm focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            aria-label="Career Match home"
          >
            <BrandLogoCompact priority className="h-9 sm:h-10" />
          </Link>

          <nav
            className="hidden items-center gap-7 font-sans text-sm font-medium text-muted-foreground md:flex"
            aria-label="Primary"
          >
            {links.map((link) =>
              link.external ? (
                <a
                  key={link.href}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-sm hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                  {link.label}
                </a>
              ) : (
                <a
                  key={link.href}
                  href={link.href}
                  className="rounded-sm hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                  {link.label}
                </a>
              ),
            )}
          </nav>

          <Link
            href="/match"
            className={cn(
              buttonVariants({ size: "lg" }),
              "font-cta h-11 shrink-0 bg-primary px-5 text-primary-foreground hover:bg-primary/90",
            )}
          >
            Try Career Match
          </Link>
        </div>

        <nav
          className="flex flex-wrap gap-x-4 gap-y-2 font-sans text-sm text-muted-foreground md:hidden"
          aria-label="Sections"
        >
          {links.map((link) =>
            link.external ? (
              <a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground"
              >
                {link.label}
              </a>
            ) : (
              <a key={link.href} href={link.href} className="hover:text-foreground">
                {link.label}
              </a>
            ),
          )}
        </nav>
      </div>
    </header>
  );
}
