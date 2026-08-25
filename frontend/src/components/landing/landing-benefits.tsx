const benefits = [
  {
    title: "Personalized Matches",
    body: "Understand how your skills align with each opportunity.",
    icon: (
      <svg viewBox="0 0 24 24" className="size-5" aria-hidden fill="none" stroke="currentColor" strokeWidth="1.75">
        <circle cx="12" cy="8" r="3.25" />
        <path d="M5.5 19.5c1.2-3.2 3.5-4.75 6.5-4.75s5.3 1.55 6.5 4.75" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Data-Driven Insights",
    body: "See why a role matches your experience.",
    icon: (
      <svg viewBox="0 0 24 24" className="size-5" aria-hidden fill="none" stroke="currentColor" strokeWidth="1.75">
        <path d="M5 19V10M12 19V5M19 19v-7" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "Better Outcomes",
    body: "Identify strengths, gaps, and next steps.",
    icon: (
      <svg viewBox="0 0 24 24" className="size-5" aria-hidden fill="none" stroke="currentColor" strokeWidth="1.75">
        <path d="M5 16l4.5-4.5L13 15l6-7" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M16 8h3v3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
];

export function LandingBenefits() {
  return (
    <section
      id="features"
      className="mx-auto w-full max-w-[1240px] px-4 pb-16 sm:px-6 lg:px-8"
      aria-labelledby="benefits-heading"
    >
      <h2 id="benefits-heading" className="sr-only">
        Benefits
      </h2>
      <div className="grid gap-4 sm:grid-cols-3 sm:gap-5">
        {benefits.map((item) => (
          <article
            key={item.title}
            className="flex items-start gap-4 rounded-2xl border border-primary/10 bg-card/80 px-5 py-5"
          >
            <div className="flex size-12 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
              {item.icon}
            </div>
            <div className="space-y-1.5">
              <h3 className="font-sans text-base font-semibold text-primary">
                {item.title}
              </h3>
              <p className="font-body text-sm leading-relaxed text-muted-foreground">
                {item.body}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
