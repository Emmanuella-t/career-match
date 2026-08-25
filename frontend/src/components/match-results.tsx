import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { MatchResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

type MatchResultsProps = {
  result: MatchResponse;
};

function formatScore(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function SkillChips({
  skills,
  emptyLabel,
  variant,
}: {
  skills: string[];
  emptyLabel: string;
  variant: "matched" | "missing" | "weak";
}) {
  if (skills.length === 0) {
    return <p className="text-sm text-muted-foreground">{emptyLabel}</p>;
  }

  return (
    <ul className="flex list-none flex-wrap gap-2 p-0" aria-label={emptyLabel}>
      {skills.map((skill) => (
        <li key={skill}>
          <Badge
            variant="outline"
            className={cn(
              "rounded-md border px-2.5 py-1 text-xs font-medium",
              variant === "matched" &&
                "border-primary/25 bg-mint text-mint-foreground",
              variant === "missing" &&
                "border-border bg-muted text-muted-foreground",
              variant === "weak" &&
                "border-action/30 bg-action/10 text-foreground",
            )}
          >
            {skill}
          </Badge>
        </li>
      ))}
    </ul>
  );
}

export function MatchResults({ result }: MatchResultsProps) {
  const hasComponentScores =
    result.semantic_score != null ||
    result.tfidf_score != null ||
    result.skill_overlap_score != null;

  const showHybridBreakdown =
    result.tfidf_score != null || result.skill_overlap_score != null;

  return (
    <Card className="border-border/80 shadow-none">
      <CardHeader className="space-y-3">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1">
            <CardTitle className="text-2xl tracking-tight">Match analysis</CardTitle>
            <CardDescription>
              Relevance of this resume to the job description.
            </CardDescription>
          </div>
          <p className="font-[family-name:var(--font-support)] text-xs uppercase tracking-[0.14em] text-muted-foreground">
            {result.matcher}
          </p>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div
          className="rounded-xl border border-primary/15 bg-card px-5 py-6"
          aria-labelledby="overall-score-label"
        >
          <p
            id="overall-score-label"
            className="font-[family-name:var(--font-support)] text-xs uppercase tracking-[0.16em] text-muted-foreground"
          >
            Relevance score
          </p>
          <p className="mt-2 font-[family-name:var(--font-heading)] text-5xl font-semibold tracking-tight text-primary tabular-nums sm:text-6xl">
            {formatScore(result.overall_score)}
            <span className="ml-1 text-2xl font-medium text-muted-foreground">
              / 100
            </span>
          </p>
          <p className="mt-3 max-w-prose font-[family-name:var(--font-serif)] text-sm leading-6 text-muted-foreground">
            {result.disclaimer}
          </p>
        </div>

        <section className="space-y-2" aria-labelledby="matched-skills-heading">
          <h3 id="matched-skills-heading" className="text-sm font-semibold">
            Matched skills
          </h3>
          <SkillChips
            skills={result.matched_skills}
            emptyLabel="No overlapping catalog skills were found."
            variant="matched"
          />
        </section>

        <section className="space-y-2" aria-labelledby="missing-skills-heading">
          <h3 id="missing-skills-heading" className="text-sm font-semibold">
            Missing skills
          </h3>
          <p className="text-xs text-muted-foreground">
            Skills mentioned in the job that were not clearly present in the resume.
          </p>
          <SkillChips
            skills={result.missing_skills}
            emptyLabel="No missing catalog skills were identified."
            variant="missing"
          />
        </section>

        {result.weak_or_negated_skills.length > 0 ? (
          <section className="space-y-2" aria-labelledby="weak-skills-heading">
            <h3 id="weak-skills-heading" className="text-sm font-semibold">
              Weak or negated skills
            </h3>
            <p className="text-xs text-muted-foreground">
              Skills with limited, weak, or negated evidence in the resume.
            </p>
            <SkillChips
              skills={result.weak_or_negated_skills}
              emptyLabel=""
              variant="weak"
            />
          </section>
        ) : null}

        {hasComponentScores && showHybridBreakdown ? (
          <>
            <Separator />
            <section
              className="space-y-3"
              aria-labelledby="score-breakdown-heading"
            >
              <h3
                id="score-breakdown-heading"
                className="text-sm font-semibold text-muted-foreground"
              >
                How this score was formed
              </h3>
              <dl className="grid gap-2 text-sm sm:grid-cols-3">
                {result.semantic_score != null ? (
                  <div className="rounded-lg bg-muted/60 px-3 py-2">
                    <dt className="text-xs text-muted-foreground">Semantic</dt>
                    <dd className="mt-0.5 font-medium tabular-nums">
                      {formatScore(result.semantic_score)}
                    </dd>
                  </div>
                ) : null}
                {result.tfidf_score != null ? (
                  <div className="rounded-lg bg-muted/60 px-3 py-2">
                    <dt className="text-xs text-muted-foreground">TF-IDF</dt>
                    <dd className="mt-0.5 font-medium tabular-nums">
                      {formatScore(result.tfidf_score)}
                    </dd>
                  </div>
                ) : null}
                {result.skill_overlap_score != null ? (
                  <div className="rounded-lg bg-muted/60 px-3 py-2">
                    <dt className="text-xs text-muted-foreground">Skill overlap</dt>
                    <dd className="mt-0.5 font-medium tabular-nums">
                      {formatScore(result.skill_overlap_score)}
                    </dd>
                  </div>
                ) : null}
              </dl>
            </section>
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

export function MatchEmptyState() {
  return (
    <Card className="border-dashed border-border/80 shadow-none">
      <CardContent className="flex min-h-64 items-center justify-center px-6 py-10">
        <p className="max-w-sm text-center text-sm leading-6 text-muted-foreground">
          Paste your resume and a job description to see your match analysis.
        </p>
      </CardContent>
    </Card>
  );
}

export function MatchLoadingState() {
  return (
    <Card className="border-border/80 shadow-none" aria-live="polite" aria-busy="true">
      <CardContent className="flex min-h-64 flex-col items-center justify-center gap-3 px-6 py-10">
        <div
          className="size-5 animate-spin rounded-full border-2 border-primary/25 border-t-primary"
          aria-hidden="true"
        />
        <p className="text-sm text-muted-foreground">Analyzing your match...</p>
      </CardContent>
    </Card>
  );
}
