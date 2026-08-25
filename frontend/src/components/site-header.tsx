"use client";

import { useAuth } from "@clerk/nextjs";
import Link from "next/link";

import { BrandLogoCompact } from "@/components/brand-mark";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Overview" },
  { href: "/match", label: "Match" },
  { href: "/architecture", label: "Architecture" },
];

export function SiteHeader() {
  const { isLoaded, isSignedIn } = useAuth();

  return (
    <header className="border-b border-border/80 bg-background/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <Link
          href="/"
          className="inline-flex w-fit items-center rounded-sm focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          aria-label="Career Match home"
        >
          <BrandLogoCompact priority />
        </Link>
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
          <nav
            className="flex flex-wrap gap-x-5 gap-y-2 font-sans text-sm text-muted-foreground"
            aria-label="Primary"
          >
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-sm hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                {link.label}
              </Link>
            ))}
          </nav>
          {isLoaded && isSignedIn ? (
            <Link
              href="/dashboard"
              className="rounded-sm text-sm font-medium text-primary hover:text-career-green focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              Dashboard
            </Link>
          ) : null}
          {isLoaded && !isSignedIn ? (
            <>
              <Link
                href="/login"
                className="rounded-sm text-sm font-medium text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                Log In
              </Link>
              <Link
                href="/match"
                className={cn(
                  buttonVariants({ size: "sm" }),
                  "bg-primary text-primary-foreground hover:bg-primary/90",
                )}
              >
                Try Career Match
              </Link>
            </>
          ) : null}
        </div>
      </div>
    </header>
  );
}
