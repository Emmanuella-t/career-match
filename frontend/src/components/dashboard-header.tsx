"use client";

import { useClerk, useUser } from "@clerk/nextjs";
import Link from "next/link";

import { BrandLogoCompact } from "@/components/brand-mark";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/jobs", label: "Discover Jobs" },
  { href: "/dashboard/tailor", label: "Tailor Resume" },
  { href: "/match", label: "New Match" },
  { href: "/dashboard#recent-matches", label: "Recent Matches" },
  { href: "/dashboard#resumes", label: "My Resumes" },
  { href: "/dashboard#history", label: "Match History" },
  { href: "/dashboard#saved-jobs", label: "Saved Jobs" },
  { href: "/dashboard#profile", label: "Profile / Settings" },
];

export function DashboardHeader() {
  const { user } = useUser();
  const { signOut } = useClerk();
  const firstName = user?.firstName?.trim();

  return (
    <header className="border-b border-border/80 bg-background/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-4 sm:px-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            href="/dashboard"
            className="inline-flex rounded-sm focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            aria-label="Career Match dashboard"
          >
            <BrandLogoCompact priority />
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            <p className="hidden text-sm text-muted-foreground sm:block">
              {firstName ? `Welcome back, ${firstName}` : "Welcome back"}
            </p>
            <Link
              href="/match"
              className={cn(
                buttonVariants({ size: "sm" }),
                "bg-action text-action-foreground hover:bg-action/90",
              )}
            >
              New Match
            </Link>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => void signOut({ redirectUrl: "/" })}
            >
              Log out
            </Button>
          </div>
        </div>
        <nav
          className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted-foreground"
          aria-label="Dashboard"
        >
          {navItems.map((item) => (
            <Link
              key={item.href + item.label}
              href={item.href}
              className="rounded-sm hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
