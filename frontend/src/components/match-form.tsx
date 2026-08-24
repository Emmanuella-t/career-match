"use client";

import { useMemo, useState, useTransition } from "react";

import { Badge } from "@/components/ui/badge";
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
import { overlapSkills } from "@/lib/skills";

const SAMPLE_RESUME = `Data analyst with 4 years of experience. Skills: Python, pandas, SQL, Git, and Linux. Built internal dashboards and documented ETL checks.`;

const SAMPLE_JOB = `We are hiring a data analyst. Required: Python, SQL, and pandas. Nice to have: Docker and AWS.`;

type Result = ReturnType<typeof overlapSkills>;

export function MatchForm() {
  const [resume, setResume] = useState("");
  const [job, setJob] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [pending, startTransition] = useTransition();

  const isEmpty = resume.trim() === "" && job.trim() === "";

  const summary = useMemo(() => {
    if (!result) return null;
    const totalJob = result.shared.length + result.jobOnly.length;
    return { totalJob };
  }, [result]);

  function runCompare() {
    setError(null);
    if (!resume.trim() || !job.trim()) {
      setResult(null);
      setError("Paste both a resume and a job description to compare skill mentions.");
      return;
    }
    startTransition(async () => {
      await new Promise((resolve) => setTimeout(resolve, 350));
      setResult(overlapSkills(resume, job));
    });
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.9fr)]">
      <Card>
        <CardHeader>
          <CardTitle>Skill overlap prototype</CardTitle>
          <CardDescription>
            This screen uses the same small lexicon as the Python package. It
            does not call a trained matcher and does not produce a hiring score.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="resume">Resume text</Label>
            <Textarea
              id="resume"
              value={resume}
              onChange={(event) => setResume(event.target.value)}
              placeholder="Paste resume text…"
              className="min-h-36"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="job">Job description</Label>
            <Textarea
              id="job"
              value={job}
              onChange={(event) => setJob(event.target.value)}
              placeholder="Paste the job description…"
              className="min-h-36"
            />
          </div>
          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
          <div className="flex flex-col gap-2 sm:flex-row">
            <Button onClick={runCompare} disabled={pending}>
              {pending ? "Comparing mentions…" : "Compare skill mentions"}
            </Button>
            <Button
              type="button"
              variant="outline"
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
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Result</CardTitle>
          <CardDescription>
            Shared mentions are overlaps in a fixed word list, not evidence of
            job performance.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {pending ? (
            <p className="text-sm text-muted-foreground">Scanning both texts…</p>
          ) : result ? (
            <div className="space-y-4">
              {summary && summary.totalJob === 0 ? (
                <p className="text-sm text-muted-foreground">
                  The job text did not mention any skills from the current
                  lexicon. That is a coverage gap in the prototype list, not a
                  candidate score.
                </p>
              ) : null}
              <SkillGroup title="Mentioned in both" skills={result.shared} />
              <SkillGroup title="Resume only" skills={result.resumeOnly} />
              <SkillGroup title="Job only" skills={result.jobOnly} />
            </div>
          ) : isEmpty ? (
            <p className="text-sm text-muted-foreground">
              Nothing to compare yet. Paste a resume and a job description, or
              load the sample pair.
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">
              Ready when both fields are filled.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function SkillGroup({ title, skills }: { title: string; skills: string[] }) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium">{title}</h3>
      {skills.length === 0 ? (
        <p className="text-sm text-muted-foreground">None in this list.</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {skills.map((skill) => (
            <Badge key={skill} variant="secondary">
              {skill}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
