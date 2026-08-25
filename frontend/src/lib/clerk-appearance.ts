/** Shared Clerk appearance tokens aligned with Career Match branding. */
export const clerkAppearance = {
  variables: {
    colorPrimary: "#173f35",
    colorDanger: "#b42318",
    colorSuccess: "#2ebb68",
    colorWarning: "#f28c52",
    colorNeutral: "#202724",
    colorText: "#202724",
    colorTextSecondary: "#68716c",
    colorBackground: "#ffffff",
    colorInputBackground: "#faf8f2",
    colorInputText: "#202724",
    borderRadius: "0.625rem",
    fontFamily: "var(--font-montserrat), Montserrat, sans-serif",
  },
  elements: {
    rootBox: "mx-auto w-full",
    card: "shadow-none border border-border bg-card",
    headerTitle: "font-headline text-primary",
    headerSubtitle: "font-body text-muted-foreground",
    formButtonPrimary:
      "bg-primary text-primary-foreground hover:bg-primary/90 font-cta",
    footerActionLink: "text-career-green hover:text-primary",
    formFieldLabel: "text-foreground font-medium",
    formFieldInput:
      "border-input focus:border-ring focus:ring-ring/50 bg-background",
    identityPreviewEditButton: "text-career-green",
  },
} as const;
