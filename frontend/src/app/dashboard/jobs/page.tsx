import { DashboardHeader } from "@/components/dashboard-header";
import { JobDiscovery } from "@/components/job-discovery";
import { SiteFooter } from "@/components/site-footer";

export default function DashboardJobsPage() {
  return (
    <>
      <DashboardHeader />
      <main className="flex-1">
        <JobDiscovery />
      </main>
      <SiteFooter />
    </>
  );
}
