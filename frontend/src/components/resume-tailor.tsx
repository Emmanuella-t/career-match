"use client";

import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useId, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import {
  clearTailorContext,
  loadTailorContext,
  saveTailorContext,
} from "@/lib/tailor-context";
import {
  listResumes,
  tailorResume,
  type ResumeTailorResponse,
  type ResumeRecord,
  type RewriteSuggestionRecord,
  type TailorTarget,
} from "@/lib/persistence-api";

function formatScore(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

const TARGET_OPTIONS: { value: TailorTarget; label: string }[] = [
  { value: "all", label: "All supported sections" },
  { value: "experience", label: "Experience bullets" },
  { value: "summary", label: "Summary" },
  { value: "projects", label: "Projects" },
  { value: "skills", label: "Skills" },
];

export function ResumeTailor() {
  const formId = useId();
  const resumeSelectId = `${formId}-resume`;
  const jobId = `${formId}-job`;
  const targetId = `${formId}-target`;

  const searchParams = useSearchParams();
  const { getToken, isLoaded, isSignedIn } = useAuth();

  const [resumes, setResumes] = useState<ResumeRecord[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [target, setTarget] = useState<TailorTarget>("all");
  const [loadingResumes, setLoadingResumes] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResumeTailorResponse | null>(null);
  const [accepted, setAccepted] = useState<Record<number, boolean>>({});
  const [copied, setCopied] = useState(false);

  const loadResumes = useCallback(async () => {
    if (!isSignedIn) return;
    setLoadingResumes(true);
    setError(null);
    try {
      const token = await getToken();
      const rows = await listResumes(token);
      setResumes(rows);

      const context = loadTailorContext();
      const resumeParam = searchParams.get("resumeId");
      const jobParam = searchParams.get("jobId");

      if (context?.resumeId) {
        setSelectedResumeId(context.resumeId);
      } else if (resumeParam) {
        setSelectedResumeId(resumeParam);
      } else if (rows.length > 0) {
        setSelectedResumeId(rows[0].id);
      }

      if (context?.jobDescription) {
        setJobDescription(context.jobDescription);
      }
      if (jobParam) {
        const { getJob } = await import("@/lib/persistence-api");
        const saved = await getJob(token, jobParam);
        setJobDescription(saved.job_description);
      }
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Could not load tailoring inputs.";
      setError(message);
    } finally {
      setLoadingResumes(false);
    }
  }, [getToken, isSignedIn, searchParams]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    /* eslint-disable-next-line react-hooks/set-state-in-effect -- async fetch on auth ready */
    void loadResumes();
  }, [isLoaded, isSignedIn, loadResumes]);

  async function runTailor() {
    if (pending || !selectedResumeId || !jobDescription.trim()) return;
    setPending(true);
    setError(null);
    setResult(null);
    setAccepted({});
    setCopied(false);

    saveTailorContext({
      resumeId: selectedResumeId,
      jobDescription,
    });

    try {
      const token = await getToken();
      const response = await tailorResume(token, {
        resume_id: selectedResumeId,
        job_description: jobDescription,
        target,
      });
      setResult(response);
      clearTailorContext();
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Could not generate tailoring suggestions. Please try again.";
      setError(message);
    } finally {
      setPending(false);
    }
  }

  function toggleAccepted(index: number) {
    setAccepted((current) => ({ ...current, [index]: !current[index] }));
  }

  async function copyAccepted() {
    if (!result) return;
    const lines = result.rewrite_suggestions
      .map((item, index) => (accepted[index] ? item.suggested_text : null))
      .filter((line): line is string => Boolean(line));
    if (!lines.length) return;
    try {
      await navigator.clipboard.writeText(lines.join("\n\n"));
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 sm:py-12">
      <div className="space-y-2">
        <p className="font-body text-sm uppercase tracking-[0.12em] text-muted-foreground">
          Grounded tailoring
        </p>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
          Tailor resume for a job
        </h1>
        <p className="max-w-3xl text-sm text-muted-foreground">
          Compare your real resume evidence to a target job, improve keyword
          alignment, and review grounded rewrite suggestions. Career Match does
          not fabricate missing experience and does not guarantee ATS passage.
        </p>
      </div>

      <Card className="border-border/80 shadow-none">
        <CardHeader>
          <CardTitle className="text-xl">Resume and job</CardTitle>
          <CardDescription>
            Select a saved resume and target job description. Your original
            resume is never overwritten automatically.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingResumes ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : resumes.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No saved resumes yet.{" "}
              <Link href="/dashboard#resumes" className="text-career-green underline-offset-4 hover:underline">
                Add a resume
              </Link>
              .
            </p>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor={resumeSelectId}>Saved resume</Label>
                  <select
                    id={resumeSelectId}
                    value={selectedResumeId}
                    onChange={(e) => setSelectedResumeId(e.target.value)}
                    disabled={pending}
                    className="h-9 w-full rounded-lg border border-input bg-card px-2.5 text-sm"
                  >
                    {resumes.map((resume) => (
                      <option key={resume.id} value={resume.id}>
                        {resume.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor={targetId}>Tailoring target</Label>
                  <select
                    id={targetId}
                    value={target}
                    onChange={(e) => setTarget(e.target.value as TailorTarget)}
                    disabled={pending}
                    className="h-9 w-full rounded-lg border border-input bg-card px-2.5 text-sm"
                  >
                    {TARGET_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor={jobId}>Job description</Label>
                <Textarea
                  id={jobId}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the target job description…"
                  className="min-h-40 resize-y bg-card"
                  disabled={pending}
                />
              </div>
              <Button
                type="button"
                disabled={pending || !selectedResumeId || !jobDescription.trim()}
                aria-busy={pending}
                className="bg-action text-action-foreground hover:bg-action/90"
                onClick={() => void runTailor()}
              >
                {pending ? "Analyzing evidence…" : "Generate tailoring suggestions"}
              </Button>
            </>
          )}
          {error ? (
            <p className="rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
        </CardContent>
      </Card>

      {result ? (
        <div className="space-y-6">
          <Card className="border-border/80 shadow-none">
            <CardHeader>
              <CardTitle className="text-xl">Keyword alignment overview</CardTitle>
              <CardDescription>{result.disclaimer}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap items-center gap-4">
                <div className="rounded-lg border border-career-green/25 bg-mint/15 px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">
                    Resume-to-job alignment
                  </p>
                  <p className="text-3xl font-semibold text-primary">
                    {formatScore(result.original_alignment_score)}
                  </p>
                </div>
                <p className="text-sm text-muted-foreground">
                  Matcher: {result.matcher}
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Supported keywords
                  </p>
                  <p className="mt-2 text-sm text-foreground">
                    {result.supported_keywords.join(", ") || "None detected"}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Missing / unsupported
                  </p>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {result.missing_requirements.join(", ") || "None flagged"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {result.warnings.length > 0 ? (
            <Card className="border-destructive/20 shadow-none">
              <CardHeader>
                <CardTitle className="text-lg">Warnings</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc space-y-2 pl-5 text-sm text-destructive">
                  {result.warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ) : null}

          <Card className="border-border/80 shadow-none">
            <CardHeader>
              <CardTitle className="text-lg">Evidence map</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {result.evidence_map.map((entry) => (
                <div key={entry.requirement} className="rounded-lg border border-border/80 p-3 text-sm">
                  <p className="font-medium text-foreground">
                    {entry.requirement}{" "}
                    <span className="text-muted-foreground">({entry.status})</span>
                  </p>
                  <p className="mt-1 text-muted-foreground">{entry.support_reason}</p>
                  {entry.supporting_text ? (
                    <p className="mt-2 rounded bg-muted/30 p-2 text-xs">
                      {entry.supporting_text}
                    </p>
                  ) : null}
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="border-border/80 shadow-none">
            <CardHeader>
              <CardTitle className="text-lg">Rewrite suggestions</CardTitle>
              <CardDescription>
                Review each suggestion. Accept changes you want, then copy revised
                text. Your saved resume stays unchanged.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {result.rewrite_suggestions.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No grounded rewrite suggestions for this target. Review the
                  evidence map and warnings above.
                </p>
              ) : (
                result.rewrite_suggestions.map((suggestion, index) => (
                  <SuggestionCard
                    key={`${suggestion.section}-${index}`}
                    suggestion={suggestion}
                    accepted={Boolean(accepted[index])}
                    onToggle={() => toggleAccepted(index)}
                  />
                ))
              )}
              {result.rewrite_suggestions.length > 0 ? (
                <Button type="button" variant="outline" onClick={() => void copyAccepted()}>
                  {copied ? "Copied accepted text" : "Copy accepted suggestions"}
                </Button>
              ) : null}
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
}

function SuggestionCard({
  suggestion,
  accepted,
  onToggle,
}: {
  suggestion: RewriteSuggestionRecord;
  accepted: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="space-y-3 rounded-lg border border-border/80 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-medium capitalize">{suggestion.section}</p>
        <Button type="button" size="sm" variant={accepted ? "default" : "outline"} onClick={onToggle}>
          {accepted ? "Accepted" : "Accept"}
        </Button>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-muted-foreground">Original</p>
        <p className="mt-1 text-sm">{suggestion.original_text}</p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-muted-foreground">Suggested</p>
        <p className="mt-1 text-sm text-primary">{suggestion.suggested_text}</p>
      </div>
      <p className="text-xs text-muted-foreground">
        {suggestion.support_reason}
        {suggestion.keywords_introduced.length
          ? ` Keywords introduced: ${suggestion.keywords_introduced.join(", ")}.`
          : ""}
      </p>
    </div>
  );
}
