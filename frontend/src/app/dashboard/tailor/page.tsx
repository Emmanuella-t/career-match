import { Suspense } from "react";

import { DashboardHeader } from "@/components/dashboard-header";
import { ResumeTailor } from "@/components/resume-tailor";
import { SiteFooter } from "@/components/site-footer";

export default function DashboardTailorPage() {
  return (
    <>
      <DashboardHeader />
      <main className="flex-1">
        <Suspense
          fallback={
            <p className="px-4 py-10 text-sm text-muted-foreground" role="status">
              Loading tailoring workspace…
            </p>
          }
        >
          <ResumeTailor />
        </Suspense>
      </main>
      <SiteFooter />
    </>
  );
}
