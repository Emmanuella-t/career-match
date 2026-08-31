"use client";

import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import {
  useCallback,
  useEffect,
  useId,
  useState,
  type FormEvent,
} from "react";

import { Button, buttonVariants } from "@/components/ui/button";
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
import { ApiError } from "@/lib/api";
import {
  createJob,
  createResume,
  deleteJob,
  deleteMatch,
  deleteResume,
  listJobs,
  listMatches,
  listResumes,
  type MatchAnalysisRecord,
  type ResumeRecord,
  type SavedJobRecord,
  updateResume,
} from "@/lib/persistence-api";
import { cn } from "@/lib/utils";

function EmptyState({ message }: { message: string }) {
  return (
    <p className="rounded-lg border border-dashed border-border bg-muted/40 px-4 py-6 text-sm text-muted-foreground">
      {message}
    </p>
  );
}

function formatScore(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function formatDate(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function DashboardHome() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const resumeNameId = useId();
  const resumeTextId = useId();
  const jobTitleId = useId();
  const jobCompanyId = useId();
  const jobDescId = useId();
  const jobUrlId = useId();
  const jobNotesId = useId();

  const [resumes, setResumes] = useState<ResumeRecord[]>([]);
  const [matches, setMatches] = useState<MatchAnalysisRecord[]>([]);
  const [jobs, setJobs] = useState<SavedJobRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<MatchAnalysisRecord | null>(
    null,
  );

  const [resumeName, setResumeName] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [editingResumeId, setEditingResumeId] = useState<string | null>(null);
  const [resumeBusy, setResumeBusy] = useState(false);

  const [jobTitle, setJobTitle] = useState("");
  const [jobCompany, setJobCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [jobUrl, setJobUrl] = useState("");
  const [jobNotes, setJobNotes] = useState("");
  const [jobBusy, setJobBusy] = useState(false);

  const refresh = useCallback(async () => {
    if (!isSignedIn) return;
    setLoading(true);
    setLoadError(null);
    try {
      const token = await getToken();
      const [resumeRows, matchRows, jobRows] = await Promise.all([
        listResumes(token),
        listMatches(token),
        listJobs(token),
      ]);
      setResumes(resumeRows);
      setMatches(matchRows);
      setJobs(jobRows);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Could not load your saved workspace data.";
      setLoadError(message);
    } finally {
      setLoading(false);
    }
  }, [getToken, isSignedIn]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    /* Load workspace data once Clerk session is ready. */
    /* eslint-disable-next-line react-hooks/set-state-in-effect -- async fetch on auth ready */
    void refresh();
  }, [isLoaded, isSignedIn, refresh]);

  async function onSaveResume(event: FormEvent) {
    event.preventDefault();
    if (resumeBusy) return;
    setResumeBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      const token = await getToken();
      if (editingResumeId) {
        await updateResume(token, editingResumeId, {
          name: resumeName,
          resume_text: resumeText,
        });
        setActionMessage("Resume updated.");
      } else {
        await createResume(token, {
          name: resumeName,
          resume_text: resumeText,
        });
        setActionMessage("Resume saved.");
      }
      setResumeName("");
      setResumeText("");
      setEditingResumeId(null);
      await refresh();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : "Could not save resume.",
      );
    } finally {
      setResumeBusy(false);
    }
  }

  async function onSaveJob(event: FormEvent) {
    event.preventDefault();
    if (jobBusy) return;
    setJobBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      const token = await getToken();
      await createJob(token, {
        title: jobTitle,
        company: jobCompany || null,
        job_description: jobDescription,
        source_url: jobUrl || null,
        notes: jobNotes || null,
      });
      setJobTitle("");
      setJobCompany("");
      setJobDescription("");
      setJobUrl("");
      setJobNotes("");
      setActionMessage("Job opportunity saved.");
      await refresh();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : "Could not save job.",
      );
    } finally {
      setJobBusy(false);
    }
  }

  const recentMatches = matches.slice(0, 5);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 sm:py-12">
      <div className="space-y-2">
        <p className="font-body text-sm uppercase tracking-[0.12em] text-muted-foreground">
          Workspace
        </p>
        <h1 className="font-headline text-3xl font-semibold tracking-tight text-primary sm:text-4xl">
          Welcome back
        </h1>
        <p className="max-w-2xl font-body text-base text-muted-foreground">
          Your saved resumes, match history, and job opportunities live here.
          Matching still runs through the same FastAPI matchers — nothing is
          invented for empty lists.
        </p>
      </div>

      <Card className="border-career-green/20 bg-[linear-gradient(135deg,_rgba(143,223,196,0.22),_rgba(250,248,242,0.9)_55%,_#ffffff)] shadow-none">
        <CardHeader>
          <CardTitle className="font-headline text-2xl tracking-tight text-primary">
            Start a New Match
          </CardTitle>
          <CardDescription>
            Analyze a resume against a job description, then save the result
            when you want it in history.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            href="/match"
            className={cn(
              buttonVariants({ size: "lg" }),
              "font-cta h-11 bg-primary px-5 text-primary-foreground hover:bg-primary/90",
            )}
          >
            Open Match →
          </Link>
        </CardContent>
      </Card>

      {loadError ? (
        <p
          className="rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive"
          role="alert"
        >
          {loadError}
        </p>
      ) : null}
      {actionError ? (
        <p
          className="rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive"
          role="alert"
        >
          {actionError}
        </p>
      ) : null}
      {actionMessage ? (
        <p className="text-sm text-primary" role="status">
          {actionMessage}
        </p>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        <section id="recent-matches" aria-labelledby="recent-matches-heading">
          <h2
            id="recent-matches-heading"
            className="font-headline text-xl font-semibold text-primary"
          >
            Recent Matches
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Your latest saved analyses.
          </p>
          <div className="mt-4 space-y-3">
            {loading ? (
              <p className="text-sm text-muted-foreground">Loading…</p>
            ) : recentMatches.length === 0 ? (
              <EmptyState message="No saved matches yet." />
            ) : (
              recentMatches.map((match) => (
                <article
                  key={match.id}
                  className="rounded-lg border border-border/80 bg-card px-4 py-3"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <h3 className="font-medium text-foreground">
                        {match.job_title || "Untitled role"}
                        {match.company ? ` · ${match.company}` : ""}
                      </h3>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {match.matcher} · {formatDate(match.created_at)}
                      </p>
                    </div>
                    <p className="font-[family-name:var(--font-support)] text-lg text-primary">
                      {formatScore(match.overall_score)}
                    </p>
                  </div>
                  {match.matched_skills.length > 0 ? (
                    <p className="mt-2 text-sm text-muted-foreground">
                      Top skills: {match.matched_skills.slice(0, 4).join(", ")}
                    </p>
                  ) : null}
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => setSelectedMatch(match)}
                    >
                      Open
                    </Button>
                    <Link
                      href="/dashboard#history"
                      className={cn(buttonVariants({ size: "sm", variant: "ghost" }))}
                    >
                      Full history
                    </Link>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        <section id="resumes" aria-labelledby="resumes-heading">
          <h2
            id="resumes-heading"
            className="font-headline text-xl font-semibold text-primary"
          >
            My Resumes
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Paste resume text, name it, and reuse it in Match.
          </p>
          <form className="mt-4 space-y-3" onSubmit={onSaveResume}>
            <div className="space-y-2">
              <Label htmlFor={resumeNameId}>Resume name</Label>
              <Input
                id={resumeNameId}
                value={resumeName}
                onChange={(event) => setResumeName(event.target.value)}
                placeholder="e.g. Product engineer 2026"
                required
                disabled={resumeBusy}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor={resumeTextId}>Resume text</Label>
              <Textarea
                id={resumeTextId}
                value={resumeText}
                onChange={(event) => setResumeText(event.target.value)}
                placeholder="Paste resume text…"
                className="min-h-32"
                required
                disabled={resumeBusy}
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <Button type="submit" disabled={resumeBusy} aria-busy={resumeBusy}>
                {editingResumeId
                  ? resumeBusy
                    ? "Updating…"
                    : "Update resume"
                  : resumeBusy
                    ? "Saving…"
                    : "Save resume"}
              </Button>
              {editingResumeId ? (
                <Button
                  type="button"
                  variant="ghost"
                  disabled={resumeBusy}
                  onClick={() => {
                    setEditingResumeId(null);
                    setResumeName("");
                    setResumeText("");
                  }}
                >
                  Cancel edit
                </Button>
              ) : null}
            </div>
          </form>
          <div className="mt-4 space-y-3">
            {loading ? (
              <p className="text-sm text-muted-foreground">Loading…</p>
            ) : resumes.length === 0 ? (
              <EmptyState message="No saved resumes yet." />
            ) : (
              resumes.map((resume) => (
                <article
                  key={resume.id}
                  className="rounded-lg border border-border/80 bg-card px-4 py-3"
                >
                  <h3 className="font-medium text-foreground">{resume.name}</h3>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Updated {formatDate(resume.updated_at)}
                  </p>
                  <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">
                    {resume.resume_text}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Link
                      href={`/match?resumeId=${resume.id}`}
                      className={cn(buttonVariants({ size: "sm" }))}
                    >
                      Use in Match
                    </Link>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setEditingResumeId(resume.id);
                        setResumeName(resume.name);
                        setResumeText(resume.resume_text);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        void (async () => {
                          setActionError(null);
                          try {
                            const token = await getToken();
                            await deleteResume(token, resume.id);
                            if (editingResumeId === resume.id) {
                              setEditingResumeId(null);
                              setResumeName("");
                              setResumeText("");
                            }
                            setActionMessage("Resume deleted.");
                            await refresh();
                          } catch (err) {
                            setActionError(
                              err instanceof ApiError
                                ? err.message
                                : "Could not delete resume.",
                            );
                          }
                        })();
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        <section id="history" aria-labelledby="history-heading">
          <h2
            id="history-heading"
            className="font-headline text-xl font-semibold text-primary"
          >
            Match History
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Saved analyses from Match. Guests are never written here.
          </p>
          <div className="mt-4 space-y-3">
            {loading ? (
              <p className="text-sm text-muted-foreground">Loading…</p>
            ) : matches.length === 0 ? (
              <EmptyState message="No match history yet." />
            ) : (
              matches.map((match) => (
                <article
                  key={match.id}
                  className="rounded-lg border border-border/80 bg-card px-4 py-3"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <h3 className="font-medium text-foreground">
                        {match.job_title || "Untitled role"}
                        {match.company ? ` · ${match.company}` : ""}
                      </h3>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Score {formatScore(match.overall_score)} · {match.matcher} ·{" "}
                        {formatDate(match.created_at)}
                      </p>
                    </div>
                  </div>
                  {match.matched_skills.length > 0 ? (
                    <p className="mt-2 text-sm text-muted-foreground">
                      Matched: {match.matched_skills.slice(0, 6).join(", ")}
                    </p>
                  ) : null}
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => setSelectedMatch(match)}
                    >
                      Open
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        void (async () => {
                          setActionError(null);
                          try {
                            const token = await getToken();
                            await deleteMatch(token, match.id);
                            if (selectedMatch?.id === match.id) {
                              setSelectedMatch(null);
                            }
                            setActionMessage("Saved analysis deleted.");
                            await refresh();
                          } catch (err) {
                            setActionError(
                              err instanceof ApiError
                                ? err.message
                                : "Could not delete analysis.",
                            );
                          }
                        })();
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        <section id="saved-jobs" aria-labelledby="saved-jobs-heading">
          <h2
            id="saved-jobs-heading"
            className="font-headline text-xl font-semibold text-primary"
          >
            Saved Opportunities
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Manually save roles to reuse in Match. No scraping in this milestone.
          </p>
          <form className="mt-4 space-y-3" onSubmit={onSaveJob}>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor={jobTitleId}>Title</Label>
                <Input
                  id={jobTitleId}
                  value={jobTitle}
                  onChange={(event) => setJobTitle(event.target.value)}
                  required
                  disabled={jobBusy}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor={jobCompanyId}>Company</Label>
                <Input
                  id={jobCompanyId}
                  value={jobCompany}
                  onChange={(event) => setJobCompany(event.target.value)}
                  disabled={jobBusy}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor={jobDescId}>Job description</Label>
              <Textarea
                id={jobDescId}
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                className="min-h-28"
                required
                disabled={jobBusy}
              />
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor={jobUrlId}>Source URL (optional)</Label>
                <Input
                  id={jobUrlId}
                  type="url"
                  value={jobUrl}
                  onChange={(event) => setJobUrl(event.target.value)}
                  placeholder="https://"
                  disabled={jobBusy}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor={jobNotesId}>Notes (optional)</Label>
                <Input
                  id={jobNotesId}
                  value={jobNotes}
                  onChange={(event) => setJobNotes(event.target.value)}
                  disabled={jobBusy}
                />
              </div>
            </div>
            <Button type="submit" disabled={jobBusy} aria-busy={jobBusy}>
              {jobBusy ? "Saving…" : "Save job"}
            </Button>
          </form>
          <div className="mt-4 space-y-3">
            {loading ? (
              <p className="text-sm text-muted-foreground">Loading…</p>
            ) : jobs.length === 0 ? (
              <EmptyState message="No saved jobs yet." />
            ) : (
              jobs.map((job) => (
                <article
                  key={job.id}
                  className="rounded-lg border border-border/80 bg-card px-4 py-3"
                >
                  <h3 className="font-medium text-foreground">
                    {job.title}
                    {job.company ? ` · ${job.company}` : ""}
                  </h3>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Updated {formatDate(job.updated_at)}
                  </p>
                  <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">
                    {job.job_description}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Link
                      href={`/match?jobId=${job.id}`}
                      className={cn(buttonVariants({ size: "sm" }))}
                    >
                      Use in Match
                    </Link>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        void (async () => {
                          setActionError(null);
                          try {
                            const token = await getToken();
                            await deleteJob(token, job.id);
                            setActionMessage("Saved job deleted.");
                            await refresh();
                          } catch (err) {
                            setActionError(
                              err instanceof ApiError
                                ? err.message
                                : "Could not delete job.",
                            );
                          }
                        })();
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      </div>

      <section id="profile" aria-labelledby="profile-heading" className="pb-4">
        <h2
          id="profile-heading"
          className="font-headline text-xl font-semibold text-primary"
        >
          Profile / Settings
        </h2>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          Account identity is managed by Clerk. Career Match stores only a
          lightweight profile row keyed to your Clerk user id (no passwords).
        </p>
        <div className="mt-4">
          <EmptyState message="No product settings configured yet." />
        </div>
      </section>

      {selectedMatch ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          role="presentation"
        >
          <button
            type="button"
            className="absolute inset-0 bg-[#202724]/45"
            aria-label="Close analysis detail"
            onClick={() => setSelectedMatch(null)}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="saved-match-title"
            className="relative z-10 max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-border bg-card p-6 shadow-[0_18px_40px_rgba(23,63,53,0.16)]"
          >
            <h2
              id="saved-match-title"
              className="font-headline text-2xl font-semibold text-primary"
            >
              {selectedMatch.job_title || "Saved analysis"}
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {selectedMatch.company ? `${selectedMatch.company} · ` : ""}
              Score {formatScore(selectedMatch.overall_score)} ·{" "}
              {selectedMatch.matcher} · {formatDate(selectedMatch.created_at)}
            </p>
            <div className="mt-4 space-y-3 text-sm">
              <div>
                <p className="font-medium text-foreground">Matched skills</p>
                <p className="text-muted-foreground">
                  {selectedMatch.matched_skills.join(", ") || "None listed"}
                </p>
              </div>
              <div>
                <p className="font-medium text-foreground">Missing skills</p>
                <p className="text-muted-foreground">
                  {selectedMatch.missing_skills.join(", ") || "None listed"}
                </p>
              </div>
              <div>
                <p className="font-medium text-foreground">Job description</p>
                <p className="whitespace-pre-wrap text-muted-foreground">
                  {selectedMatch.job_description}
                </p>
              </div>
            </div>
            <div className="mt-6">
              <Button type="button" onClick={() => setSelectedMatch(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
