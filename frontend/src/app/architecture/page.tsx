import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const layers = [
  {
    title: "Product",
    body: "This Next.js app. Recruiter-facing copy, empty/error states, and a lexicon overlap demo. No trained weights.",
  },
  {
    title: "Serving",
    body: "Not implemented. A future API will version models and keep the UI from importing Python directly.",
  },
  {
    title: "ML",
    body: "src/career_match in the repo root. Dataset loading, parsing, extraction, matcher protocol, evaluation helpers.",
  },
];

export default function ArchitecturePage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 sm:py-14">
      <div className="max-w-3xl space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">Architecture</h1>
        <p className="text-muted-foreground">
          Career Match keeps research, serving, and product in separate layers.
          The ML package can change without a UI rewrite; the UI cannot silently
          become the model.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {layers.map((layer) => (
          <Card key={layer.title}>
            <CardHeader>
              <CardTitle>{layer.title}</CardTitle>
              <CardDescription>{layer.body}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Current ML status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm leading-6 text-muted-foreground">
          <p>
            No production matching model has been implemented. The next
            milestone is a measurable resume-to-job baseline, with a frozen
            split, before semantic embedding models.
          </p>
          <p>
            Full write-up: docs/architecture.md and docs/model-card.md in the
            repository root.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
