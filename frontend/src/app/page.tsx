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

export default function HomePage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-4 py-10 sm:px-6 sm:py-14">
      <section className="max-w-3xl space-y-4">
        <p className="font-[family-name:var(--font-support)] text-xs uppercase tracking-[0.16em] text-muted-foreground">
          Explainable resume matching
        </p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-5xl">
          Career Match
        </h1>
        <p className="max-w-2xl text-base leading-7 text-muted-foreground">
          Score a resume against a job description with clear skill evidence.
          The product UI calls the FastAPI matching service and shows matched,
          missing, and weak or negated skills—without treating the score as a
          hiring decision.
        </p>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Link
            href="/match"
            className={cn(
              buttonVariants({ size: "lg" }),
              "bg-action text-action-foreground hover:bg-action/90",
            )}
          >
            Analyze a match
          </Link>
          <Link
            href="/architecture"
            className={buttonVariants({ variant: "outline", size: "lg" })}
          >
            Read the architecture
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Card className="border-border/80 shadow-none">
          <CardHeader>
            <CardTitle>ML package</CardTitle>
            <CardDescription>
              Lexical, semantic, and hybrid matchers with development and holdout
              benchmarks.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Scores are 0–100 relevance signals evaluated on synthetic fixtures,
            not production hiring models.
          </CardContent>
        </Card>
        <Card className="border-border/80 shadow-none">
          <CardHeader>
            <CardTitle>Matching API</CardTitle>
            <CardDescription>
              FastAPI exposes POST /api/v1/match with semantic as the default
              matcher.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Run the backend locally, then use this UI to inspect real analysis
            results.
          </CardContent>
        </Card>
        <Card className="border-border/80 shadow-none">
          <CardHeader>
            <CardTitle>This UI</CardTitle>
            <CardDescription>
              Paste resume and job text, analyze, and review explainable
              results.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            No fake demo scores. PDF/DOCX parsing is not claimed in this
            milestone.
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
