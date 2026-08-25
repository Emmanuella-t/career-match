import { BrandIcon } from "@/components/brand-mark";

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-border/80">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-4 py-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div className="flex items-center gap-2">
          <BrandIcon className="size-5 opacity-90" />
          <p>Explainable resume-to-job matching.</p>
        </div>
        <p>Relevance scores are not hiring probabilities.</p>
      </div>
    </footer>
  );
}
