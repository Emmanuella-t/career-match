import Image from "next/image";

import { cn } from "@/lib/utils";

const BRAND = {
  logo: "/brand/career-match-logo.svg",
  horizontal: "/brand/career-match-horizontal-logo.svg",
  icon: "/brand/career-match-icon.svg",
} as const;

type BrandMarkProps = {
  className?: string;
  priority?: boolean;
};

/** Full primary lockup (icon + wordmark). Light-background use only. */
export function BrandLogo({ className, priority = false }: BrandMarkProps) {
  return (
    <Image
      src={BRAND.logo}
      alt="Career Match"
      width={1264}
      height={290}
      priority={priority}
      className={cn("h-auto w-full max-w-md object-contain object-left", className)}
      unoptimized
    />
  );
}

/** Compact horizontal lockup for navigation. */
export function BrandLogoCompact({ className, priority = false }: BrandMarkProps) {
  return (
    <Image
      src={BRAND.horizontal}
      alt="Career Match"
      width={1148}
      height={216}
      priority={priority}
      className={cn("h-8 w-auto object-contain object-left sm:h-9", className)}
      unoptimized
    />
  );
}

/** CM icon mark only. */
export function BrandIcon({ className }: BrandMarkProps) {
  return (
    <Image
      src={BRAND.icon}
      alt=""
      width={128}
      height={128}
      className={cn("size-6 object-contain", className)}
      unoptimized
      aria-hidden
    />
  );
}
