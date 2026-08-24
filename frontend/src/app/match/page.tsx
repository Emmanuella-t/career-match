import { MatchForm } from "@/components/match-form";

export default function MatchPage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-10 sm:px-6 sm:py-14">
      <div className="max-w-3xl space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">Prototype</h1>
        <p className="text-muted-foreground">
          Use this page to inspect skill mentions. It is not a production
          matcher and it does not recommend hire or reject.
        </p>
      </div>
      <MatchForm />
    </div>
  );
}
