#!/usr/bin/env python3
"""Developer CLI for Baseline Matcher v0.1.

Compare resume text to job-description text and print the structured result.
This is not an HTTP API and not a hiring tool.
"""

from __future__ import annotations

import argparse
import json
import sys

from career_match.matching import BaselineMatcher
from career_match.matching.config import MATCHER_NAME

SAMPLE_RESUME = (
    "Backend Engineer shipping REST APIs with Python, FastAPI, Django, and SQL. "
    "Services run in Docker on AWS Linux hosts. Git-based reviews."
)
SAMPLE_JOB = (
    "Backend Engineer for REST APIs in Python using FastAPI or Django, SQL, "
    "Docker, AWS, Linux, and Git."
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", help="Resume text. Ignored when --sample is set.")
    parser.add_argument("--job", help="Job description text. Ignored when --sample is set.")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Run the built-in backend engineer sample pair.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print a JSON object instead of text.",
    )
    return parser.parse_args(argv)


def _result_payload(resume_text: str, job_text: str) -> dict[str, object]:
    result = BaselineMatcher().match(resume_text, job_text)
    return {
        "matcher": MATCHER_NAME,
        "overall_score": round(result.overall_score, 2),
        "tfidf_similarity": round(result.tfidf_similarity, 2),
        "skill_overlap_score": round(result.skill_overlap_score, 2),
        "matched_skills": list(result.matched_skills),
        "missing_skills": list(result.missing_skills),
        "resume_skills": list(result.resume_skills),
        "job_skills": list(result.job_skills),
        "evidence": list(result.evidence),
        "note": "Baseline relevance score on 0-100. Not a hiring probability.",
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.sample:
        resume_text, job_text = SAMPLE_RESUME, SAMPLE_JOB
    else:
        if not args.resume or not args.job:
            print("Provide --resume and --job, or pass --sample.", file=sys.stderr)
            return 2
        resume_text, job_text = args.resume, args.job

    payload = _result_payload(resume_text, job_text)
    if args.as_json:
        print(json.dumps(payload, indent=2))
        return 0

    print(f"{payload['matcher']}")
    print(f"overall_score:        {payload['overall_score']}")
    print(f"tfidf_similarity:     {payload['tfidf_similarity']}")
    print(f"skill_overlap_score:  {payload['skill_overlap_score']}")
    print(f"matched_skills:       {', '.join(payload['matched_skills']) or '(none)'}")
    print(f"missing_skills:       {', '.join(payload['missing_skills']) or '(none)'}")
    print(f"resume_skills:        {', '.join(payload['resume_skills']) or '(none)'}")
    print(f"job_skills:           {', '.join(payload['job_skills']) or '(none)'}")
    print("note: Baseline relevance score on 0-100. Not a hiring probability.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
