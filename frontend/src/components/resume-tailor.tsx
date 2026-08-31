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
  applyTailorRevision,
  exportTailoredResume,
  listResumes,
  tailorResume,
  type ResumeTailorApplyResponse,
  type ResumeTailorResponse,
  type ResumeRecord,
  type RewriteSuggestionRecord,
  type TailorTarget,
} from "@/lib/persistence-api";

type TailorStep = "analyze" | "review" | "preview" | "export";

const STEPS: { id: TailorStep; label: string }[] = [
  { id: "analyze", label: "Analyze" },
  { id: "review", label: "Review suggestions" },
  { id: "preview", label: "Preview revision" },
  { id: "export", label: "Export" },
];

function formatScore(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function formatDelta(value: number): string {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${formatScore(value)}`;
}

const TARGET_OPTIONS: { value: TailorTarget; label: string }[] = [
  { value: "all", label: "All supported sections" },
  { value: "experience", label: "Experience bullets" },
  { value: "summary", label: "Summary" },
  { value: "projects", label: "Projects" },
  { value: "skills", label: "Skills" },
];

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function ResumeTailor() {
  const formId = useId();
  const resumeSelectId = `${formId}-resume`;
  const jobId = `${formId}-job`;
  const targetId = `${formId}-target`;

  const searchParams = useSearchParams();
  const { getToken, isLoaded, isSignedIn } = useAuth();

  const [step, setStep] = useState<TailorStep>("analyze");
  const [resumes, setResumes] = useState<ResumeRecord[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [target, setTarget] = useState<TailorTarget>("all");
  const [loadingResumes, setLoadingResumes] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResumeTailorResponse | null>(null);
  const [accepted, setAccepted] = useState<Record<string, boolean>>({});
  const [preview, setPreview] = useState<ResumeTailorApplyResponse | null>(null);
  const [exporting, setExporting] = useState<"docx" | "txt" | null>(null);

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
    setPreview(null);
    setAccepted({});

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
      setStep("review");
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

  function toggleAccepted(suggestionId: string) {
    setAccepted((current) => ({
      ...current,
      [suggestionId]: !current[suggestionId],
    }));
    setPreview(null);
  }

  function acceptedIds(): string[] {
    if (!result) return [];
    return result.rewrite_suggestions
      .filter((item) => accepted[item.suggestion_id])
      .map((item) => item.suggestion_id);
  }

  async function runPreview() {
    if (!result || pending) return;
    setPending(true);
    setError(null);
    try {
      const token = await getToken();
      const response = await applyTailorRevision(token, {
        resume_id: selectedResumeId,
        job_description: jobDescription,
        target,
        accepted_suggestion_ids: acceptedIds(),
      });
      setPreview(response);
      setStep("preview");
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Could not preview the revised resume.";
      setError(message);
    } finally {
      setPending(false);
    }
  }

  async function runExport(format: "docx" | "txt") {
    if (!result || exporting) return;
    setExporting(format);
    setError(null);
    try {
      const token = await getToken();
      const { blob, filename } = await exportTailoredResume(token, {
        resume_id: selectedResumeId,
        job_description: jobDescription,
        target,
        accepted_suggestion_ids: acceptedIds(),
        format,
      });
      downloadBlob(blob, filename);
      setStep("export");
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Could not export tailored resume.";
      setError(message);
    } finally {
      setExporting(null);
    }
  }

  const stepIndex = STEPS.findIndex((item) => item.id === step);

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
          Compare your real resume evidence to a target job, accept grounded
          rewrite suggestions, preview alignment changes, and export a tailored
          resume. Career Match does not fabricate missing experience and does not
          guarantee ATS passage. Review exported text before applying.
        </p>
      </div>

      <StepIndicator current={step} />

      <Card className="border-border/80 shadow-none">
        <CardHeader>
          <CardTitle className="text-xl">
            {step === "analyze" ? "Resume and job" : "Workflow"}
          </CardTitle>
          <CardDescription>
            {step === "analyze"
              ? "Select a saved resume and target job description. Your original resume is never overwritten."
              : "Move through analyze → review → preview → export. Suggestions are not auto-accepted."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {step === "analyze" ? (
            <>
              {loadingResumes ? (
                <p className="text-sm text-muted-foreground">Loading…</p>
              ) : resumes.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No saved resumes yet.{" "}
                  <Link
                    href="/dashboard#resumes"
                    className="text-career-green underline-offset-4 hover:underline"
                  >
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
                        onChange={(e) =>
                          setTarget(e.target.value as TailorTarget)
                        }
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
                    disabled={
                      pending || !selectedResumeId || !jobDescription.trim()
                    }
                    aria-busy={pending}
                    className="bg-action text-action-foreground hover:bg-action/90"
                    onClick={() => void runTailor()}
                  >
                    {pending ? "Analyzing evidence…" : "Step 1: Analyze"}
                  </Button>
                </>
              )}
            </>
          ) : null}

          {step !== "analyze" && result ? (
            <div className="flex flex-wrap gap-2">
              {STEPS.slice(1).map((item) => (
                <Button
                  key={item.id}
                  type="button"
                  size="sm"
                  variant={step === item.id ? "default" : "outline"}
                  disabled={
                    (item.id === "preview" || item.id === "export") &&
                    result.rewrite_suggestions.length > 0 &&
                    stepIndex < 1
                  }
                  onClick={() => {
                    if (item.id === "review") setStep("review");
                    if (item.id === "preview") void runPreview();
                    if (item.id === "export") setStep("export");
                  }}
                >
                  {item.label}
                </Button>
              ))}
              <Button
                type="button"
                size="sm"
                variant="ghost"
                onClick={() => {
                  setStep("analyze");
                  setResult(null);
                  setPreview(null);
                  setAccepted({});
                }}
              >
                Start over
              </Button>
            </div>
          ) : null}

          {error ? (
            <p
              className="rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive"
              role="alert"
            >
              {error}
            </p>
          ) : null}
        </CardContent>
      </Card>

      {result && step !== "analyze" ? (
        <div className="space-y-6">
          <AlignmentOverview result={result} preview={preview} />

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

          {step === "review" ? (
            <>
              <Card className="border-border/80 shadow-none">
                <CardHeader>
                  <CardTitle className="text-lg">Evidence map</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {result.evidence_map.map((entry) => (
                    <div
                      key={entry.requirement}
                      className="rounded-lg border border-border/80 p-3 text-sm"
                    >
                      <p className="font-medium text-foreground">
                        {entry.requirement}{" "}
                        <span className="text-muted-foreground">
                          ({entry.status})
                        </span>
                      </p>
                      <p className="mt-1 text-muted-foreground">
                        {entry.support_reason}
                      </p>
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
                  <CardTitle className="text-lg">
                    Step 2: Review suggestions
                  </CardTitle>
                  <CardDescription>
                    Accept only changes grounded in your resume evidence. Nothing
                    is applied until you preview or export.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {result.rewrite_suggestions.length === 0 ? (
                    <p className="text-sm text-muted-foreground">
                      No grounded rewrite suggestions for this target.
                    </p>
                  ) : (
                    result.rewrite_suggestions.map((suggestion) => (
                      <SuggestionCard
                        key={suggestion.suggestion_id}
                        suggestion={suggestion}
                        accepted={Boolean(accepted[suggestion.suggestion_id])}
                        onToggle={() => toggleAccepted(suggestion.suggestion_id)}
                      />
                    ))
                  )}
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      disabled={pending}
                      onClick={() => void runPreview()}
                    >
                      {pending ? "Building preview…" : "Step 3: Preview revision"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : null}

          {step === "preview" && preview ? (
            <Card className="border-border/80 shadow-none">
              <CardHeader>
                <CardTitle className="text-lg">Revised resume preview</CardTitle>
                <CardDescription>
                  Structured sections reflect accepted suggestions only. Original
                  saved resume is unchanged.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      Newly covered keywords
                    </p>
                    <p className="mt-2 text-sm">
                      {preview.newly_covered_keywords.join(", ") || "None"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      Remaining gaps
                    </p>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {preview.remaining_missing_requirements.join(", ") ||
                        "None flagged"}
                    </p>
                  </div>
                </div>
                <pre className="max-h-[28rem] overflow-auto rounded-lg border border-border/80 bg-muted/20 p-4 text-xs whitespace-pre-wrap">
                  {preview.revised_resume_text}
                </pre>
                <div className="flex flex-wrap gap-2">
                  <Button type="button" variant="outline" onClick={() => setStep("review")}>
                    Back to review
                  </Button>
                  <Button type="button" onClick={() => setStep("export")}>
                    Continue to export
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : null}

          {step === "export" ? (
            <Card className="border-border/80 shadow-none">
              <CardHeader>
                <CardTitle className="text-lg">Step 4: Export</CardTitle>
                <CardDescription>
                  Download an ATS-friendly DOCX or plain-text resume. Review the
                  file before submitting applications.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  disabled={exporting !== null}
                  onClick={() => void runExport("docx")}
                >
                  {exporting === "docx" ? "Preparing DOCX…" : "Export DOCX"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  disabled={exporting !== null}
                  onClick={() => void runExport("txt")}
                >
                  {exporting === "txt" ? "Preparing TXT…" : "Export TXT"}
                </Button>
                {!preview ? (
                  <Button
                    type="button"
                    variant="ghost"
                    disabled={pending}
                    onClick={() => void runPreview()}
                  >
                    Refresh preview first
                  </Button>
                ) : null}
              </CardContent>
            </Card>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function StepIndicator({ current }: { current: TailorStep }) {
  const currentIndex = STEPS.findIndex((step) => step.id === current);
  return (
    <ol className="flex flex-wrap gap-2 text-sm">
      {STEPS.map((step, index) => (
        <li
          key={step.id}
          className={
            index <= currentIndex
              ? "rounded-full bg-mint/30 px-3 py-1 text-primary"
              : "rounded-full border border-border/80 px-3 py-1 text-muted-foreground"
          }
        >
          {index + 1}. {step.label}
        </li>
      ))}
    </ol>
  );
}

function AlignmentOverview({
  result,
  preview,
}: {
  result: ResumeTailorResponse;
  preview: ResumeTailorApplyResponse | null;
}) {
  return (
    <Card className="border-border/80 shadow-none">
      <CardHeader>
        <CardTitle className="text-xl">Alignment comparison</CardTitle>
        <CardDescription>
          {preview?.disclaimer ?? result.disclaimer}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <ScoreBlock label="Original alignment" value={result.original_alignment_score} />
          {preview ? (
            <>
              <ScoreBlock label="Revised alignment" value={preview.revised_alignment_score} />
              <div className="rounded-lg border border-border/80 px-4 py-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  Change
                </p>
                <p className="text-2xl font-semibold text-primary">
                  {formatDelta(preview.alignment_delta)}
                </p>
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">
              Accept suggestions and preview to see revised alignment.
            </p>
          )}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Supported keywords (original)
            </p>
            <p className="mt-2 text-sm text-foreground">
              {result.supported_keywords.join(", ") || "None detected"}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Missing / unsupported (original)
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              {result.missing_requirements.join(", ") || "None flagged"}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ScoreBlock({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-career-green/25 bg-mint/15 px-4 py-3">
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="text-3xl font-semibold text-primary">{formatScore(value)}</p>
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
        <Button
          type="button"
          size="sm"
          variant={accepted ? "default" : "outline"}
          onClick={onToggle}
        >
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
