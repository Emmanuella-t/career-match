"use client";

import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useId, useState } from "react";

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
import { ApiError } from "@/lib/api";
import { saveMatchDraft } from "@/lib/match-draft";
import { saveTailorContext } from "@/lib/tailor-context";
import {
  createJob,
  discoverJobs,
  listResumes,
  type RankedJobResult,
  type ResumeRecord,
} from "@/lib/persistence-api";

function formatScore(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function topSkills(skills: string[], count = 4): string[] {
  return skills.slice(0, count);
}

export function JobDiscovery() {
  const formId = useId();
  const resumeSelectId = `${formId}-resume`;
  const locationId = `${formId}-location`;
  const employmentId = `${formId}-employment`;

  const router = useRouter();
  const { getToken, isLoaded, isSignedIn } = useAuth();

  const [resumes, setResumes] = useState<ResumeRecord[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [location, setLocation] = useState("");
  const [employmentType, setEmploymentType] = useState("");
  const [loadingResumes, setLoadingResumes] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<RankedJobResult[]>([]);
  const [disclaimer, setDisclaimer] = useState<string | null>(null);
  const [sourceName, setSourceName] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<Record<string, "idle" | "saving" | "saved" | "error">>(
    {},
  );

  const loadResumes = useCallback(async () => {
    if (!isSignedIn) return;
    setLoadingResumes(true);
    setError(null);
    try {
      const token = await getToken();
      const rows = await listResumes(token);
      setResumes(rows);
      if (rows.length > 0) {
        setSelectedResumeId((current) => current || rows[0].id);
      }
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Could not load your saved resumes.";
      setError(message);
    } finally {
      setLoadingResumes(false);
    }
  }, [getToken, isSignedIn]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    /* Load resumes once Clerk session is ready. */
    /* eslint-disable-next-line react-hooks/set-state-in-effect -- async fetch on auth ready */
    void loadResumes();
  }, [isLoaded, isSignedIn, loadResumes]);

  async function runDiscover() {
    if (pending || !selectedResumeId) return;
    setPending(true);
    setError(null);
    setResults([]);
    setDisclaimer(null);
    setSourceName(null);
    setSaveState({});

    try {
      const token = await getToken();
      const response = await discoverJobs(token, {
        resume_id: selectedResumeId,
        location: location.trim() || undefined,
        employment_type: employmentType.trim() || undefined,
      });
      setResults(response.results);
      setDisclaimer(response.disclaimer);
      setSourceName(response.source);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Could not rank jobs for this resume. Please try again.";
      setError(message);
    } finally {
      setPending(false);
    }
  }

  function tailorForJob(result: RankedJobResult) {
    saveTailorContext({
      resumeId: selectedResumeId,
      jobDescription: result.job.description,
      jobTitle: result.job.title,
    });
    router.push(
      `/dashboard/tailor?resumeId=${encodeURIComponent(selectedResumeId)}`,
    );
  }

  function viewMatch(result: RankedJobResult) {
    const resume = resumes.find((row) => row.id === selectedResumeId);
    if (!resume) return;
    saveMatchDraft({
      resume: resume.resume_text,
      job: result.job.description,
      matcher: "semantic",
    });
    router.push(`/match?resumeId=${encodeURIComponent(selectedResumeId)}`);
  }

  async function saveJob(result: RankedJobResult) {
    const jobId = result.job.id;
    setSaveState((current) => ({ ...current, [jobId]: "saving" }));
    try {
      const token = await getToken();
      await createJob(token, {
        title: result.job.title,
        company: result.job.company,
        job_description: result.job.description,
        source_url: result.job.source_url ?? result.job.apply_url,
        notes: `Discovered via ${result.job.source}`,
      });
      setSaveState((current) => ({ ...current, [jobId]: "saved" }));
    } catch {
      setSaveState((current) => ({ ...current, [jobId]: "error" }));
    }
  }

  const selectedResume = resumes.find((row) => row.id === selectedResumeId);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 sm:py-12">
      <div className="space-y-2">
        <p className="font-body text-sm uppercase tracking-[0.12em] text-muted-foreground">
          Job discovery
        </p>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
          Find matching jobs
        </h1>
        <p className="max-w-3xl text-sm text-muted-foreground">
          Choose one of your saved resumes to rank available job opportunities by
          the same evidence-aware matcher used on the Match page. Scores reflect
          resume-to-job relevance, not hiring probability.
        </p>
      </div>

      <Card className="border-border/80 shadow-none">
        <CardHeader>
          <CardTitle className="text-xl">Resume and filters</CardTitle>
          <CardDescription>
            Discovery is authenticated and uses your saved resumes. Add a resume
            on the dashboard if you need a new profile.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingResumes ? (
            <p className="text-sm text-muted-foreground">Loading resumes…</p>
          ) : resumes.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border bg-muted/40 px-4 py-6 text-sm text-muted-foreground">
              No saved resumes yet.{" "}
              <Link
                href="/dashboard#resumes"
                className="font-medium text-career-green underline-offset-4 hover:underline"
              >
                Add a resume
              </Link>{" "}
              or{" "}
              <Link
                href="/match"
                className="font-medium text-career-green underline-offset-4 hover:underline"
              >
                analyze a match
              </Link>{" "}
              first.
            </div>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2 md:col-span-1">
                  <Label htmlFor={resumeSelectId}>Saved resume</Label>
                  <select
                    id={resumeSelectId}
                    value={selectedResumeId}
                    onChange={(event) => setSelectedResumeId(event.target.value)}
                    disabled={pending}
                    className="h-9 w-full rounded-lg border border-input bg-card px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {resumes.map((resume) => (
                      <option key={resume.id} value={resume.id}>
                        {resume.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor={locationId}>Location filter (optional)</Label>
                  <Input
                    id={locationId}
                    value={location}
                    onChange={(event) => setLocation(event.target.value)}
                    placeholder="e.g. Remote"
                    disabled={pending}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor={employmentId}>Employment type (optional)</Label>
                  <Input
                    id={employmentId}
                    value={employmentType}
                    onChange={(event) => setEmploymentType(event.target.value)}
                    placeholder="e.g. full-time"
                    disabled={pending}
                  />
                </div>
              </div>
              {selectedResume ? (
                <p className="text-xs text-muted-foreground">
                  Using resume &ldquo;{selectedResume.name}&rdquo; (
                  {selectedResume.resume_text.length.toLocaleString()} characters).
                </p>
              ) : null}
              <Button
                type="button"
                disabled={pending || !selectedResumeId}
                aria-busy={pending}
                className="bg-action text-action-foreground hover:bg-action/90"
                onClick={() => void runDiscover()}
              >
                {pending ? "Ranking jobs…" : "Find matching jobs"}
              </Button>
            </>
          )}
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

      {pending ? (
        <Card className="border-border/80 shadow-none">
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Ranking available jobs with the semantic matcher…
          </CardContent>
        </Card>
      ) : null}

      {!pending && results.length === 0 && sourceName ? (
        <Card className="border-border/80 shadow-none">
          <CardContent className="py-10 text-center">
            <p className="text-sm font-medium text-foreground">
              No job source is configured yet.
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              The discovery catalog is empty until a real job provider sync is
              connected. You can still save jobs manually from your dashboard.
            </p>
          </CardContent>
        </Card>
      ) : null}

      {!pending && results.length > 0 ? (
        <div className="space-y-4">
          <div className="space-y-1">
            <h2 className="text-xl font-semibold tracking-tight">
              Ranked opportunities
            </h2>
            {disclaimer ? (
              <p className="text-xs text-muted-foreground">{disclaimer}</p>
            ) : null}
          </div>
          <div className="grid gap-4">
            {results.map((result) => {
              const saveStatus = saveState[result.job.id] ?? "idle";
              const strengths = topSkills(result.matched_skills);
              const gaps = topSkills(result.missing_skills, 3);
              return (
                <Card key={result.job.id} className="border-border/80 shadow-none">
                  <CardHeader className="gap-3">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">{result.job.title}</CardTitle>
                        <CardDescription>
                          {[result.job.company, result.job.location]
                            .filter(Boolean)
                            .join(" · ") || "Company not listed"}
                          {result.job.employment_type
                            ? ` · ${result.job.employment_type}`
                            : ""}
                        </CardDescription>
                      </div>
                      <div className="rounded-lg border border-career-green/25 bg-mint/15 px-3 py-2 text-center">
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">
                          Relevance
                        </p>
                        <p className="text-2xl font-semibold text-primary">
                          {formatScore(result.overall_score)}
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                          Strongest matches
                        </p>
                        {strengths.length ? (
                          <ul className="mt-2 flex flex-wrap gap-2">
                            {strengths.map((skill) => (
                              <li
                                key={skill}
                                className="rounded-full bg-mint/20 px-2.5 py-1 text-xs text-primary"
                              >
                                {skill}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="mt-2 text-sm text-muted-foreground">
                            No strong skill overlap detected.
                          </p>
                        )}
                      </div>
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                          Notable gaps
                        </p>
                        {gaps.length ? (
                          <ul className="mt-2 flex flex-wrap gap-2">
                            {gaps.map((skill) => (
                              <li
                                key={skill}
                                className="rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground"
                              >
                                {skill}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="mt-2 text-sm text-muted-foreground">
                            No major missing skills flagged.
                          </p>
                        )}
                      </div>
                    </div>

                    {result.weak_or_negated_skills.length > 0 ? (
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                          Weak or negated evidence
                        </p>
                        <p className="mt-2 text-sm text-muted-foreground">
                          {result.weak_or_negated_skills.slice(0, 4).join(", ")}
                        </p>
                      </div>
                    ) : null}

                    <div className="grid gap-2 text-xs text-muted-foreground sm:grid-cols-3">
                      {result.semantic_score !== null ? (
                        <p>Semantic: {formatScore(result.semantic_score)}</p>
                      ) : null}
                      {result.tfidf_score !== null ? (
                        <p>TF-IDF: {formatScore(result.tfidf_score)}</p>
                      ) : null}
                      {result.skill_overlap_score !== null ? (
                        <p>Skill overlap: {formatScore(result.skill_overlap_score)}</p>
                      ) : null}
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => tailorForJob(result)}
                      >
                        Tailor resume
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => viewMatch(result)}
                      >
                        View match
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        disabled={saveStatus === "saving" || saveStatus === "saved"}
                        onClick={() => void saveJob(result)}
                      >
                        {saveStatus === "saving"
                          ? "Saving…"
                          : saveStatus === "saved"
                            ? "Saved"
                            : "Save job"}
                      </Button>
                      {result.job.source_url ? (
                        <a
                          href={result.job.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex h-9 items-center rounded-lg border border-input px-3 text-sm hover:bg-muted/40"
                        >
                          Source listing
                        </a>
                      ) : null}
                    </div>
                    {saveStatus === "error" ? (
                      <p className="text-sm text-destructive" role="alert">
                        Could not save this job. Try again from your dashboard.
                      </p>
                    ) : null}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
}
