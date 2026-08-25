import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-4 py-10 sm:px-6 sm:py-14">
      <section className="max-w-3xl space-y-4">
        <p className="text-sm font-medium text-muted-foreground">
          ML-first resume matching
        </p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Career Match scores a resume against a job with evidence a recruiter
          can inspect.
        </h1>
        <p className="max-w-2xl text-base leading-7 text-muted-foreground">
          This repository started as a Resume Screening notebook that classified
          resumes into job families. The product direction is different: one
          resume, one job description, an explainable match. That matcher is
          not built yet.
        </p>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Link href="/match" className={buttonVariants()}>
            Open the skill-overlap prototype
          </Link>
          <Link
            href="/architecture"
            className={buttonVariants({ variant: "outline" })}
          >
            Read the architecture
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>ML package</CardTitle>
            <CardDescription>
              Python modules for data, parsing, extraction, matching contracts,
              and evaluation helpers.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Matching raises an explicit not-implemented error until a measured
            baseline exists.
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Legacy prototype</CardTitle>
            <CardDescription>
              The original notebook, 169-row CSV, and cover image live under
              legacy/.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Category classification is preserved as history, not as a hiring
            score.
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>This UI</CardTitle>
            <CardDescription>
              Product shell for future serving. It does not host model weights.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            The compare screen only highlights lexicon overlaps so the layers
            stay honest.
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
