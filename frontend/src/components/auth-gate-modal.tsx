"use client";

import Link from "next/link";
import { useEffect, useId, useRef } from "react";

import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type AuthGateReason = "guest_limit" | "upload_required";

type AuthGateModalProps = {
  open: boolean;
  reason?: AuthGateReason;
  onClose: () => void;
  loginHref: string;
  signupHref: string;
};

const AUTH_GATE_COPY: Record<
  AuthGateReason,
  { title: string; description: string }
> = {
  guest_limit: {
    title: "Keep matching with Career Match",
    description:
      "You've completed your free guest analyses. Create a free account or log in to continue and keep your match history in one place.",
  },
  upload_required: {
    title: "Sign in to upload a resume file",
    description:
      "PDF and DOCX parsing is available for signed-in users. Create a free account or log in to upload a file, or continue by pasting resume text as a guest.",
  },
};

export function AuthGateModal({
  open,
  reason = "guest_limit",
  onClose,
  loginHref,
  signupHref,
}: AuthGateModalProps) {
  const titleId = useId();
  const descriptionId = useId();
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    dialogRef.current?.focus();

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  const copy = AUTH_GATE_COPY[reason];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="presentation"
    >
      <button
        type="button"
        className="absolute inset-0 bg-[#202724]/45"
        aria-label="Dismiss authentication prompt"
        onClick={onClose}
      />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
        tabIndex={-1}
        className="relative z-10 w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-[0_18px_40px_rgba(23,63,53,0.16)] outline-none sm:p-8"
      >
        <h2
          id={titleId}
          className="font-headline text-2xl font-semibold tracking-tight text-primary sm:text-3xl"
        >
          {copy.title}
        </h2>
        <p
          id={descriptionId}
          className="mt-3 font-body text-base leading-relaxed text-muted-foreground"
        >
          {copy.description}
        </p>
        {reason === "guest_limit" ? (
          <p className="mt-2 text-sm text-muted-foreground">
            Your current resume and job description stay on this device so you can
            continue after signing in.
          </p>
        ) : null}

        <div className="mt-6 flex flex-col gap-3">
          <Link
            href={signupHref}
            className={cn(
              buttonVariants({ size: "lg" }),
              "font-cta h-11 justify-center bg-primary text-primary-foreground hover:bg-primary/90",
            )}
          >
            Create Account
          </Link>
          <Link
            href={loginHref}
            className={cn(
              buttonVariants({ size: "lg", variant: "outline" }),
              "font-cta h-11 justify-center",
            )}
          >
            Log In
          </Link>
          <Button
            type="button"
            variant="ghost"
            className="h-10 text-muted-foreground"
            onClick={onClose}
          >
            Not now
          </Button>
        </div>
      </div>
    </div>
  );
}
