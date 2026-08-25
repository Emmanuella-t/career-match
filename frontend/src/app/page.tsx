import { LandingBenefits } from "@/components/landing/landing-benefits";
import { LandingFinalCta } from "@/components/landing/landing-final-cta";
import { LandingFooter } from "@/components/landing/landing-footer";
import { LandingHero } from "@/components/landing/landing-hero";
import { LandingHowItWorks } from "@/components/landing/landing-how-it-works";
import { LandingNavbar } from "@/components/landing/landing-navbar";
import { LandingProductPreview } from "@/components/landing/landing-product-preview";
import { LandingWhyCareerMatch } from "@/components/landing/landing-why";

export default function HomePage() {
  return (
    <>
      <LandingNavbar />
      <main>
        <LandingHero />
        <LandingBenefits />
        <LandingHowItWorks />
        <LandingProductPreview />
        <LandingWhyCareerMatch />
        <LandingFinalCta />
      </main>
      <LandingFooter />
    </>
  );
}
