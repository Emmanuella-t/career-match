import { MatchForm } from "@/components/match-form";

export default function MatchPage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-10 sm:px-6 sm:py-14">
      <div className="max-w-3xl space-y-2">
        <h1 className="font-headline text-3xl font-semibold tracking-tight sm:text-4xl">
          Resume–job match
        </h1>
        <p className="font-body text-sm uppercase tracking-[0.12em] text-muted-foreground">
          Explainable relevance analysis
        </p>
        <p className="font-body text-muted-foreground">
          Career Match scores how well a resume aligns with a job description
          and surfaces matched, missing, and weak skill evidence. Scores are
          relevance signals, not hiring decisions.
        </p>
      </div>
      <MatchForm />
    </div>
  );
}
