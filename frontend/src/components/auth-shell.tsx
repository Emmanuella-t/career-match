import Link from "next/link";

import { BrandLogoCompact } from "@/components/brand-mark";

export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <div className="relative flex min-h-full flex-1 flex-col bg-[radial-gradient(ellipse_at_top,_rgba(143,223,196,0.28),_transparent_55%),linear-gradient(180deg,_#faf8f2_0%,_#e8f2ec_100%)]">
      <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-4 py-10 sm:px-6">
        <Link
          href="/"
          className="mb-8 inline-flex w-fit rounded-sm focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          aria-label="Career Match home"
        >
          <BrandLogoCompact priority />
        </Link>

        <div className="rounded-2xl border border-border/80 bg-card/95 p-6 shadow-[0_18px_40px_rgba(23,63,53,0.08)] sm:p-8">
          <h1 className="font-headline text-3xl font-semibold tracking-tight text-primary">
            {title}
          </h1>
          <p className="mt-2 font-body text-base text-muted-foreground">
            {subtitle}
          </p>
          <div className="mt-6">{children}</div>
        </div>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          {footer}
        </p>
      </div>
    </div>
  );
}
