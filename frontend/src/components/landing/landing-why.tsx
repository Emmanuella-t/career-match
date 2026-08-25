const reasons = [
  {
    title: "Semantic Matching",
    body: "Career Match understands related skills and experience beyond exact keyword overlap.",
  },
  {
    title: "Evidence-Based Evaluation",
    body: "Matching approaches are evaluated against controlled development benchmarks rather than relying only on arbitrary scores.",
  },
  {
    title: "Actionable Feedback",
    body: "Users can see aligned skills, missing skills, and areas where evidence is weak.",
  },
];

export function LandingWhyCareerMatch() {
  return (
    <section
      id="about"
      className="border-y border-primary/10 bg-card/50 py-16 sm:py-20"
      aria-labelledby="why-heading"
    >
      <div className="mx-auto w-full max-w-[1240px] px-4 sm:px-6 lg:px-8">
        <h2
          id="why-heading"
          className="font-headline max-w-2xl text-3xl font-bold tracking-tight text-primary sm:text-4xl lg:text-5xl"
        >
          Why Career Match
        </h2>
        <p className="font-body mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg">
          Built for clarity—not hiring decisions. Scores are relevance signals
          you can inspect.
        </p>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {reasons.map((item, index) => (
            <article
              key={item.title}
              className="rounded-3xl border border-primary/10 bg-card p-7 shadow-[0_12px_24px_rgba(23,63,53,0.05)]"
            >
              <div className="mb-5 flex size-12 items-center justify-center rounded-2xl bg-mint/40 font-sans text-sm font-bold text-primary">
                {String(index + 1).padStart(2, "0")}
              </div>
              <h3 className="font-sans text-xl font-semibold text-primary">
                {item.title}
              </h3>
              <p className="font-body mt-3 text-base leading-relaxed text-muted-foreground">
                {item.body}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
