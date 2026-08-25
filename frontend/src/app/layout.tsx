import type { Metadata } from "next";
import {
  League_Spartan,
  Literata,
  Montserrat,
  Noto_Serif,
  Oswald,
} from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";

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

const notoSerif = Noto_Serif({
  variable: "--font-noto-serif",
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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider
      signInUrl="/login"
      signUpUrl="/signup"
      afterSignOutUrl="/"
    >
      <html
        lang="en"
        className={`${montserrat.variable} ${leagueSpartan.variable} ${oswald.variable} ${literata.variable} ${notoSerif.variable} h-full scroll-smooth antialiased`}
      >
        <body className="flex min-h-full flex-col bg-background font-sans text-foreground">
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
