import { Badge } from "@/components/ui/badge";

const strongSkills = ["Python", "Machine Learning", "Data Analysis", "SQL"];
const missingSkills = ["Kubernetes", "Production ML deployment"];

/** Marketing preview only — not a live evaluation result. */
export function LandingProductPreview() {
  return (
    <section
      id="preview"
      className="mx-auto w-full max-w-[1240px] px-4 py-16 sm:px-6 sm:py-20 lg:px-8"
      aria-labelledby="preview-heading"
    >
      <div className="mb-8 max-w-2xl space-y-3">
        <p className="font-body text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">
          Product preview
        </p>
        <h2
          id="preview-heading"
          className="font-headline text-3xl font-bold tracking-tight text-primary sm:text-4xl lg:text-5xl"
        >
          Clear scores. Clear evidence.
        </h2>
        <p className="font-body text-base leading-relaxed text-muted-foreground sm:text-lg">
          The real match experience surfaces relevance, aligned skills, and gaps
          in one readable analysis.
        </p>
      </div>

      <div className="rounded-3xl border border-primary/10 bg-card p-6 shadow-[0_12px_28px_rgba(23,63,53,0.06)] sm:p-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-sans text-xl font-semibold text-primary sm:text-2xl">
            Match analysis
          </h3>
          <span className="rounded-full border border-primary/15 bg-secondary px-3 py-1 font-sans text-xs font-medium text-primary">
            Example analysis
          </span>
        </div>

        <div className="rounded-2xl border border-primary/15 bg-background px-5 py-6 sm:px-6">
          <p className="font-body text-xs tracking-[0.16em] text-muted-foreground uppercase">
            Relevance score
          </p>
          <p className="mt-2 font-sans text-5xl font-semibold tracking-tight text-primary tabular-nums sm:text-6xl">
            92
            <span className="ml-1 text-2xl font-medium text-muted-foreground">
              / 100
            </span>
          </p>
          <p className="font-body mt-3 max-w-prose text-sm leading-6 text-muted-foreground">
            This sample reflects how Career Match presents resume-to-job
            relevance. It is not a hiring probability and not a live model
            result.
          </p>
        </div>

        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <div className="space-y-3">
            <h4 className="font-sans text-sm font-semibold text-primary">
              Strong Matches
            </h4>
            <p className="font-body text-xs text-muted-foreground">
              Skills Alignment
            </p>
            <ul className="flex list-none flex-wrap gap-2 p-0">
              {strongSkills.map((skill) => (
                <li key={skill}>
                  <Badge
                    variant="outline"
                    className="rounded-md border-primary/25 bg-mint px-2.5 py-1 text-xs font-medium text-mint-foreground"
                  >
                    {skill}
                  </Badge>
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="font-sans text-sm font-semibold text-primary">
              Missing Skills
            </h4>
            <p className="font-body text-xs text-muted-foreground">
              Opportunities to strengthen
            </p>
            <ul className="flex list-none flex-wrap gap-2 p-0">
              {missingSkills.map((skill) => (
                <li key={skill}>
                  <Badge
                    variant="outline"
                    className="rounded-md border-border bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground"
                  >
                    {skill}
                  </Badge>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-primary/10 pt-6">
          <h4 className="font-sans text-sm font-semibold text-primary">
            Resume Insights
          </h4>
          <p className="font-body mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            Strong evidence for core analytics skills. Weak or missing evidence
            for container orchestration and production ML operations in this
            example.
          </p>
        </div>
      </div>
    </section>
  );
}
