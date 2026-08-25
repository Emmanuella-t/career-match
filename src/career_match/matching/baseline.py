"""Explainable TF-IDF + skill-overlap baseline matcher (v0.1)."""

from __future__ import annotations

from career_match.core.types import MatchResult
from career_match.extraction.skills import extract_skill_names
from career_match.matching.config import MATCHER_NAME, BaselineConfig
from career_match.matching.tfidf import tfidf_cosine_similarity


def _clip_score(value: float, scale: float) -> float:
    return min(scale, max(0.0, value))


def skill_overlap(resume_skills: tuple[str, ...], job_skills: tuple[str, ...]) -> tuple[
    float, tuple[str, ...], tuple[str, ...]
]:
    """Return job-skill coverage in ``[0, 1]``, matched skills, and missing skills.

    Coverage is ``|resume ∩ job| / |job|``. If the job lists no catalog skills,
    coverage is 0.0 and both matched and missing lists are empty.
    """
    resume_set = set(resume_skills)
    job_set = set(job_skills)
    matched = tuple(skill for skill in job_skills if skill in resume_set)
    missing = tuple(skill for skill in job_skills if skill not in resume_set)
    if not job_set:
        return 0.0, (), ()
    return len(matched) / len(job_set), matched, missing


class BaselineMatcher:
    """Hybrid lexical baseline. Not a calibrated hiring model."""

    name = MATCHER_NAME

    def __init__(self, config: BaselineConfig | None = None) -> None:
        self.config = config or BaselineConfig()

    def match(self, resume_text: str, job_text: str) -> MatchResult:
        """Score one resume against one job description.

        The returned ``overall_score`` is a **baseline relevance score** on
        0–100. It is not a probability that a recruiter should hire.
        """
        config = self.config
        tfidf = tfidf_cosine_similarity(resume_text, job_text)
        resume_skills = extract_skill_names(resume_text)
        job_skills = extract_skill_names(job_text)
        overlap_unit, matched, missing = skill_overlap(resume_skills, job_skills)

        tfidf_score = tfidf * config.score_scale
        skill_score = overlap_unit * config.score_scale

        if job_skills:
            overall = (
                config.tfidf_weight * tfidf_score + config.skill_overlap_weight * skill_score
            )
            mix_note = (
                f"hybrid {config.tfidf_weight:.2f}*tfidf + "
                f"{config.skill_overlap_weight:.2f}*skill_overlap"
            )
        else:
            overall = tfidf_score
            mix_note = "job text has no catalog skills; overall score equals TF-IDF"

        evidence = (
            f"{MATCHER_NAME}: {mix_note}",
            f"tfidf_similarity={tfidf_score:.1f}/{config.score_scale:.0f}",
            f"skill_overlap={skill_score:.1f}/{config.score_scale:.0f} "
            f"({len(matched)}/{len(job_skills)} job catalog skills)",
            "Not a hiring probability.",
        )
        return MatchResult(
            overall_score=_clip_score(overall, config.score_scale),
            tfidf_similarity=_clip_score(tfidf_score, config.score_scale),
            skill_overlap_score=_clip_score(skill_score, config.score_scale),
            matched_skills=matched,
            missing_skills=missing,
            resume_skills=resume_skills,
            job_skills=job_skills,
            evidence=evidence,
        )
