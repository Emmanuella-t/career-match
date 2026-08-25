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
    body: "This Next.js app. Users paste a resume and job description, then review relevance results returned by the API.",
  },
  {
    title: "Serving",
    body: "FastAPI career_match.api. POST /api/v1/match scores text with semantic, hybrid, or lexical matchers.",
  },
  {
    title: "ML",
    body: "src/career_match in the repo root. Matching, extraction, evaluation, and frozen benchmarks.",
  },
];

export default function ArchitecturePage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 sm:py-14">
      <div className="max-w-3xl space-y-3">
        <h1 className="font-headline text-3xl font-semibold tracking-tight">
          Architecture
        </h1>
        <p className="font-body text-muted-foreground">
          Career Match keeps product, serving, and ML in separate layers. The UI
          never imports model weights; it calls the HTTP matching service.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {layers.map((layer) => (
          <Card key={layer.title} className="border-border/80 shadow-none">
            <CardHeader>
              <CardTitle>{layer.title}</CardTitle>
              <CardDescription>{layer.body}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
      <Card className="border-border/80 shadow-none">
        <CardHeader>
          <CardTitle>End-to-end flow</CardTitle>
        </CardHeader>
        <CardContent className="font-body space-y-2 text-sm leading-6 text-muted-foreground">
          <p>
            Next.js UI → FastAPI <code className="font-sans">/api/v1/match</code>{" "}
            → selected matcher → structured relevance and skill explainability →
            results UI.
          </p>
          <p>
            Default matcher is Semantic Matcher v0.1. Scores are relevance
            signals, not hiring probabilities. Full write-up:
            docs/architecture.md and docs/model-card.md.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
