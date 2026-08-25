import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

function EmptyState({ message }: { message: string }) {
  return (
    <p className="rounded-lg border border-dashed border-border bg-muted/40 px-4 py-6 text-sm text-muted-foreground">
      {message}
    </p>
  );
}

export function DashboardHome() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 sm:py-12">
      <div className="space-y-2">
        <p className="font-body text-sm uppercase tracking-[0.12em] text-muted-foreground">
          Workspace
        </p>
        <h1 className="font-headline text-3xl font-semibold tracking-tight text-primary sm:text-4xl">
          Welcome back
        </h1>
        <p className="max-w-2xl font-body text-base text-muted-foreground">
          Start a new resume–job analysis anytime. Saved history, resumes, and
          jobs will appear here once persistence is added.
        </p>
      </div>

      <Card className="border-career-green/20 bg-[linear-gradient(135deg,_rgba(143,223,196,0.22),_rgba(250,248,242,0.9)_55%,_#ffffff)] shadow-none">
        <CardHeader>
          <CardTitle className="font-headline text-2xl tracking-tight text-primary">
            Start a New Match
          </CardTitle>
          <CardDescription>
            Use the same explainable matcher flow as guest mode — without the
            two-analysis limit.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            href="/match"
            className={cn(
              buttonVariants({ size: "lg" }),
              "font-cta h-11 bg-primary px-5 text-primary-foreground hover:bg-primary/90",
            )}
          >
            Open Match →
          </Link>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <section id="recent-matches" aria-labelledby="recent-matches-heading">
          <h2
            id="recent-matches-heading"
            className="font-headline text-xl font-semibold text-primary"
          >
            Recent Matches
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Your latest analyses will list here.
          </p>
          <div className="mt-4">
            <EmptyState message="No saved matches yet." />
          </div>
        </section>

        <section id="resumes" aria-labelledby="resumes-heading">
          <h2
            id="resumes-heading"
            className="font-headline text-xl font-semibold text-primary"
          >
            Resume Profile
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Stored resumes are not available in this milestone.
          </p>
          <div className="mt-4">
            <EmptyState message="No saved resumes yet." />
          </div>
        </section>

        <section id="history" aria-labelledby="history-heading">
          <h2
            id="history-heading"
            className="font-headline text-xl font-semibold text-primary"
          >
            Match History
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Full history requires server-side persistence.
          </p>
          <div className="mt-4">
            <EmptyState message="No match history yet." />
          </div>
        </section>

        <section id="saved-jobs" aria-labelledby="saved-jobs-heading">
          <h2
            id="saved-jobs-heading"
            className="font-headline text-xl font-semibold text-primary"
          >
            Saved Opportunities
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Job saves are not wired to storage yet.
          </p>
          <div className="mt-4">
            <EmptyState message="No saved jobs yet." />
          </div>
        </section>
      </div>

      <section id="profile" aria-labelledby="profile-heading" className="pb-4">
        <h2
          id="profile-heading"
          className="font-headline text-xl font-semibold text-primary"
        >
          Profile / Settings
        </h2>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          Account identity is managed by Clerk. Application preferences and
          stored profile data will appear here in a later milestone.
        </p>
        <div className="mt-4">
          <EmptyState message="No product settings configured yet." />
        </div>
      </section>
    </div>
  );
}
