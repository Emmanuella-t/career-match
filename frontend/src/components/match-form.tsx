"use client";

import { useId, useState } from "react";

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
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  MatchApiError,
  type MatcherName,
  type MatchResponse,
  matchResumeToJob,
} from "@/lib/api";

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

  const [resume, setResume] = useState("");
  const [job, setJob] = useState("");
  const [matcher, setMatcher] = useState<MatcherName>("semantic");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [pending, setPending] = useState(false);

  async function runAnalyze() {
    if (pending) return;

    setError(null);

    if (!resume.trim() || !job.trim()) {
      setResult(null);
      setError("Paste both a resume and a job description to analyze the match.");
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

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
      <Card className="border-border/80 shadow-none">
        <CardHeader>
          <CardTitle className="text-2xl tracking-tight">Analyze a match</CardTitle>
          <CardDescription>
            Paste resume text and a job description. Career Match returns a
            relevance score with skill evidence from the selected matcher.
          </CardDescription>
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
                  onChange={(event) => setResume(event.target.value)}
                  placeholder="Paste the full resume text…"
                  className="min-h-56 resize-y bg-card md:min-h-72"
                  disabled={pending}
                  aria-invalid={Boolean(error) && !resume.trim()}
                />
                <p className="text-xs text-muted-foreground">
                  Paste text for this milestone. PDF/DOCX upload is not supported
                  yet.
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

            <div className="space-y-2">
              <Label htmlFor={matcherId} className="text-xs text-muted-foreground">
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
              <p className="rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive" role="alert">
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
                  setError(null);
                  setResult(null);
                }}
              >
                Load sample pair
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <div className="min-w-0">
        {pending ? (
          <MatchLoadingState />
        ) : result ? (
          <MatchResults result={result} />
        ) : (
          <MatchEmptyState />
        )}
      </div>
    </div>
  );
}
