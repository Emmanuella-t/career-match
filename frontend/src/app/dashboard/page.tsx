import { DashboardHeader } from "@/components/dashboard-header";
import { DashboardHome } from "@/components/dashboard-home";
import { SiteFooter } from "@/components/site-footer";

export default function DashboardPage() {
  return (
    <>
      <DashboardHeader />
      <main className="flex-1">
        <DashboardHome />
      </main>
      <SiteFooter />
    </>
  );
}
