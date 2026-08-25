"use client";

import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useId, useState } from "react";

import { AuthGateModal } from "@/components/auth-gate-modal";
import {
  MatchEmptyState,
  MatchLoadingState,
  MatchResults,
} from "@/components/match-results";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  ApiError,
  MatchApiError,
  type MatcherName,
  type MatchResponse,
  matchResumeToJob,
} from "@/lib/api";
import {
  clearGuestUsageOnAuth,
  getGuestAnalysisCount,
  getRemainingGuestAnalyses,
  GUEST_ANALYSIS_LIMIT,
  recordSuccessfulGuestAnalysis,
  shouldGateGuestAnalysis,
} from "@/lib/guest-usage";
import {
  clearMatchDraft,
  loadMatchDraft,
  saveMatchDraft,
} from "@/lib/match-draft";
import {
  buildSaveMatchPayload,
  getJob,
  getResume,
  saveMatchAnalysis,
} from "@/lib/persistence-api";

const SAMPLE_RESUME = `Jordan Lee
Machine Learning Engineer

Experience
- Built recommendation and ranking features with Python, scikit-learn, and pandas.
- Deployed FastAPI services with Docker and monitored jobs on Linux.
- Collaborated with data scientists on SQL feature pipelines and Git workflows.

Skills
Python, pandas, scikit-learn, SQL, Docker, FastAPI, Git, Linux`;

const SAMPLE_JOB = `Machine Learning Engineer

We are looking for an engineer who can ship reliable ML features.

Required:
- Strong Python and scikit-learn experience
- Comfort with SQL and pandas for feature work
- Experience deploying services with Docker

Nice to have:
- FastAPI, Git, and Linux production support`;

const MATCHER_OPTIONS: { value: MatcherName; label: string }[] = [
  { value: "semantic", label: "Semantic" },
  { value: "hybrid", label: "Hybrid" },
  { value: "lexical", label: "Lexical baseline" },
];

export function MatchForm() {
  const formId = useId();
  const resumeId = `${formId}-resume`;
  const jobId = `${formId}-job`;
  const matcherId = `${formId}-matcher`;
  const jobTitleId = `${formId}-job-title`;
  const companyId = `${formId}-company`;

  const searchParams = useSearchParams();
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const authenticated = Boolean(isSignedIn);

  const [resume, setResume] = useState("");
  const [job, setJob] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);
  const [matcher, setMatcher] = useState<MatcherName>("semantic");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [pending, setPending] = useState(false);
  const [authGateOpen, setAuthGateOpen] = useState(false);
  const [guestCount, setGuestCount] = useState(0);
  const [savePending, setSavePending] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    /* Restore client-only draft + guest usage after mount (SSR has no storage). */
    /* eslint-disable react-hooks/set-state-in-effect */
    const draft = loadMatchDraft();
    if (draft) {
      setResume(draft.resume);
      setJob(draft.job);
      setMatcher(draft.matcher);
    }
    setGuestCount(getGuestAnalysisCount());
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  useEffect(() => {
    if (!isLoaded || !authenticated) return;
    clearGuestUsageOnAuth();
    /* eslint-disable-next-line react-hooks/set-state-in-effect -- sync UI after clearing guest storage */
    setGuestCount(0);
  }, [isLoaded, authenticated]);

  useEffect(() => {
    if (!isLoaded || !authenticated) return;

    const resumeParam = searchParams.get("resumeId");
    const jobParam = searchParams.get("jobId");
    if (!resumeParam && !jobParam) return;

    let cancelled = false;

    async function loadSaved() {
      try {
        const token = await getToken();
        if (!token || cancelled) return;

        if (resumeParam) {
          const saved = await getResume(token, resumeParam);
          if (cancelled) return;
          setResume(saved.resume_text);
          setSelectedResumeId(saved.id);
        }
        if (jobParam) {
          const saved = await getJob(token, jobParam);
          if (cancelled) return;
          setJob(saved.job_description);
          setJobTitle(saved.title);
          setCompany(saved.company ?? "");
        }
      } catch (err) {
        if (cancelled) return;
        const message =
          err instanceof ApiError
            ? err.message
            : "Could not load the saved resume or job.";
        setError(message);
      }
    }

    void loadSaved();
    return () => {
      cancelled = true;
    };
  }, [authenticated, getToken, isLoaded, searchParams]);

  const closeAuthGate = useCallback(() => {
    setAuthGateOpen(false);
  }, []);

  async function runAnalyze() {
    if (pending) return;

    setError(null);
    setSaveMessage(null);
    setSaveError(null);

    if (!resume.trim() || !job.trim()) {
      setResult(null);
      setError("Paste both a resume and a job description to analyze the match.");
      return;
    }

    const draft = { resume, job, matcher };
    saveMatchDraft(draft);

    if (shouldGateGuestAnalysis(authenticated)) {
      setAuthGateOpen(true);
      return;
    }

    setPending(true);
    setResult(null);

    try {
      const response = await matchResumeToJob({
        resume_text: resume,
        job_description: job,
        matcher,
      });
      setResult(response);
      if (!authenticated) {
        const next = recordSuccessfulGuestAnalysis();
        setGuestCount(next);
      }
      clearMatchDraft();
    } catch (err) {
      setResult(null);
      if (err instanceof MatchApiError) {
        setError(err.message);
      } else {
        setError(
          "Career Match couldn't complete the analysis. Please try again.",
        );
      }
    } finally {
      setPending(false);
    }
  }

  async function runSaveAnalysis() {
    if (!result || !authenticated || savePending) return;
    setSavePending(true);
    setSaveError(null);
    setSaveMessage(null);
    try {
      const token = await getToken();
      await saveMatchAnalysis(
        token,
        buildSaveMatchPayload({
          result,
          jobDescription: job,
          jobTitle,
          company,
          resumeId: selectedResumeId,
        }),
      );
      setSaveMessage("Analysis saved to your match history.");
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Could not save this analysis. Your results are still visible above.";
      setSaveError(message);
    } finally {
      setSavePending(false);
    }
  }

  const remaining = authenticated
    ? null
    : getRemainingGuestAnalyses(guestCount);
  const returnPath = encodeURIComponent("/match");

  return (
    <>
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
        <Card className="border-border/80 shadow-none">
          <CardHeader>
            <CardTitle className="text-2xl tracking-tight">
              Analyze a match
            </CardTitle>
            <CardDescription>
              Paste resume text and a job description. Career Match returns a
              relevance score with skill evidence from the selected matcher.
            </CardDescription>
            {isLoaded && !authenticated ? (
              <p
                className="mt-2 rounded-lg border border-career-green/25 bg-mint/15 px-3 py-2 text-sm text-primary"
                role="status"
              >
                Guest mode:{" "}
                {remaining === 0
                  ? `you've used your ${GUEST_ANALYSIS_LIMIT} free analyses. Log in or sign up to continue.`
                  : `${remaining} of ${GUEST_ANALYSIS_LIMIT} free analyses remaining.`}
              </p>
            ) : null}
            {isLoaded && authenticated ? (
              <p className="mt-2 text-sm text-muted-foreground" role="status">
                Signed in — analyses are not saved automatically. Use{" "}
                <span className="font-medium text-foreground">Save analysis</span>{" "}
                after a result if you want it in your history.{" "}
                <Link
                  href="/dashboard#resumes"
                  className="font-medium text-career-green underline-offset-4 hover:underline"
                >
                  Manage resumes
                </Link>
              </p>
            ) : null}
          </CardHeader>
          <CardContent>
            <form
              className="space-y-5"
              onSubmit={(event) => {
                event.preventDefault();
                void runAnalyze();
              }}
            >
              <div className="grid gap-5 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor={resumeId}>Resume text</Label>
                  <Textarea
                    id={resumeId}
                    value={resume}
                    onChange={(event) => {
                      setResume(event.target.value);
                      setSelectedResumeId(null);
                    }}
                    placeholder="Paste the full resume text…"
                    className="min-h-56 resize-y bg-card md:min-h-72"
                    disabled={pending}
                    aria-invalid={Boolean(error) && !resume.trim()}
                  />
                  <p className="text-xs text-muted-foreground">
                    Paste text for this milestone. PDF/DOCX upload is not
                    supported yet.
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor={jobId}>Job description</Label>
                  <Textarea
                    id={jobId}
                    value={job}
                    onChange={(event) => setJob(event.target.value)}
                    placeholder="Paste the full job posting…"
                    className="min-h-56 resize-y bg-card md:min-h-72"
                    disabled={pending}
                    aria-invalid={Boolean(error) && !job.trim()}
                  />
                </div>
              </div>

              {authenticated ? (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor={jobTitleId}>Job title (optional)</Label>
                    <Input
                      id={jobTitleId}
                      value={jobTitle}
                      onChange={(event) => setJobTitle(event.target.value)}
                      placeholder="e.g. Machine Learning Engineer"
                      disabled={pending}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor={companyId}>Company (optional)</Label>
                    <Input
                      id={companyId}
                      value={company}
                      onChange={(event) => setCompany(event.target.value)}
                      placeholder="e.g. Acme"
                      disabled={pending}
                    />
                  </div>
                </div>
              ) : null}

              <div className="space-y-2">
                <Label
                  htmlFor={matcherId}
                  className="text-xs text-muted-foreground"
                >
                  Matcher (advanced)
                </Label>
                <select
                  id={matcherId}
                  value={matcher}
                  onChange={(event) =>
                    setMatcher(event.target.value as MatcherName)
                  }
                  disabled={pending}
                  className="h-9 w-full max-w-xs rounded-lg border border-input bg-card px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {MATCHER_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {error ? (
                <p
                  className="rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive"
                  role="alert"
                >
                  {error}
                </p>
              ) : null}

              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <Button
                  type="submit"
                  size="lg"
                  disabled={pending}
                  className="bg-action text-action-foreground hover:bg-action/90"
                  aria-busy={pending}
                >
                  {pending ? "Analyzing…" : "Analyze Match"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  disabled={pending}
                  onClick={() => {
                    setResume(SAMPLE_RESUME);
                    setJob(SAMPLE_JOB);
                    setSelectedResumeId(null);
                    setError(null);
                    setResult(null);
                    setSaveMessage(null);
                    setSaveError(null);
                  }}
                >
                  Load sample pair
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <div className="min-w-0 space-y-4">
          {pending ? (
            <MatchLoadingState />
          ) : result ? (
            <>
              <MatchResults result={result} />
              {authenticated ? (
                <div className="space-y-2">
                  <Button
                    type="button"
                    variant="outline"
                    disabled={savePending}
                    aria-busy={savePending}
                    onClick={() => void runSaveAnalysis()}
                  >
                    {savePending ? "Saving…" : "Save analysis"}
                  </Button>
                  {saveMessage ? (
                    <p className="text-sm text-primary" role="status">
                      {saveMessage}{" "}
                      <Link
                        href="/dashboard#history"
                        className="font-medium text-career-green underline-offset-4 hover:underline"
                      >
                        View history
                      </Link>
                    </p>
                  ) : null}
                  {saveError ? (
                    <p className="text-sm text-destructive" role="alert">
                      {saveError}
                    </p>
                  ) : null}
                </div>
              ) : null}
            </>
          ) : (
            <MatchEmptyState />
          )}
        </div>
      </div>

      <AuthGateModal
        open={authGateOpen}
        onClose={closeAuthGate}
        loginHref={`/login?redirect_url=${returnPath}`}
        signupHref={`/signup?redirect_url=${returnPath}`}
      />
    </>
  );
}
