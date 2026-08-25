import type { Metadata } from "next";
import {
  Geist_Mono,
  League_Spartan,
  Literata,
  Montserrat,
  Oswald,
} from "next/font/google";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

import "./globals.css";

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
});

const leagueSpartan = League_Spartan({
  variable: "--font-league-spartan",
  subsets: ["latin"],
});

const oswald = Oswald({
  variable: "--font-oswald",
  subsets: ["latin"],
});

const literata = Literata({
  variable: "--font-literata",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Career Match",
  description:
    "Explainable resume-to-job matching with relevance scores and skill evidence.",
  icons: {
    icon: [
      { url: "/brand/career-match-favicon.svg", type: "image/svg+xml" },
      { url: "/brand/career-match-favicon.ico", sizes: "any" },
    ],
    apple: [{ url: "/brand/career-match-apple-touch-icon.png", sizes: "256x256" }],
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${montserrat.variable} ${leagueSpartan.variable} ${oswald.variable} ${literata.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-background text-foreground">
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
