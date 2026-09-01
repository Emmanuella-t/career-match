const steps = [
  {
    number: "01",
    title: "Add your resume",
    body: "Paste resume text on /match, or sign in to upload a PDF or DOCX file.",
  },
  {
    number: "02",
    title: "Add a job description",
    body: "Provide the opportunity you want to evaluate.",
  },
  {
    number: "03",
    title: "Understand your alignment",
    body: "See a match score, supported skills, missing requirements, and explainable evidence.",
  },
];

export function LandingHowItWorks() {
  return (
    <section
      id="how-it-works"
      className="border-y border-primary/10 bg-card/50 py-16 sm:py-20"
      aria-labelledby="how-it-works-heading"
    >
      <div className="mx-auto w-full max-w-[1240px] px-4 sm:px-6 lg:px-8">
        <h2
          id="how-it-works-heading"
          className="font-headline max-w-2xl text-3xl font-bold tracking-tight text-primary sm:text-4xl lg:text-5xl"
        >
          From resume to insight in three steps.
        </h2>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {steps.map((step) => (
            <article
              key={step.number}
              className="rounded-3xl border border-primary/10 bg-card p-7 shadow-[0_12px_24px_rgba(23,63,53,0.05)]"
            >
              <div className="mb-5 flex size-11 items-center justify-center rounded-full bg-primary font-sans text-sm font-bold text-primary-foreground">
                {step.number}
              </div>
              <h3 className="font-sans text-xl font-semibold text-primary">
                {step.title}
              </h3>
              <p className="font-body mt-3 text-base leading-relaxed text-muted-foreground">
                {step.body}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
