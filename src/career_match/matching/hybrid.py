"""Hybrid Matcher v0.1: semantic + TF-IDF + evidence-aware skill coverage.

Combines independent signals. Overall score is a development relevance
score on 0–100, not a hiring probability. Weights are selected on
development benchmark v0.2 only.
"""

from __future__ import annotations

from career_match.core.types import MatchResult
from career_match.extraction.evidence import (
    STUFFING_OVERALL_FACTOR,
    build_evidence_profile,
    evidence_weighted_overlap,
)
from career_match.extraction.skills import extract_skill_names
from career_match.matching.hybrid_config import HYBRID_MATCHER_NAME, HybridConfig
from career_match.matching.semantic import SemanticMatcher
from career_match.matching.semantic_config import SemanticConfig
from career_match.matching.tfidf import tfidf_cosine_similarity


def _clip_score(value: float, scale: float) -> float:
    return min(scale, max(0.0, value))


class HybridMatcher:
    """Evidence-aware hybrid of semantic, lexical, and skill channels."""

    name = HYBRID_MATCHER_NAME

    def __init__(
        self,
        config: HybridConfig | None = None,
        semantic_matcher: SemanticMatcher | None = None,
    ) -> None:
        self.config = config or HybridConfig()
        self.semantic_matcher = semantic_matcher or SemanticMatcher(SemanticConfig())

    def match(self, resume_text: str, job_text: str) -> MatchResult:
        """Score one resume against one job with three observable channels.

        Returned ``overall_score`` is a **hybrid relevance score** on 0–100.
        It is not a probability that a recruiter should hire.
        """
        config = self.config
        semantic_result = self.semantic_matcher.match(resume_text, job_text)
        semantic_score = semantic_result.semantic_similarity

        tfidf_unit = tfidf_cosine_similarity(resume_text, job_text)
        tfidf_score = tfidf_unit * config.score_scale

        job_skills = extract_skill_names(job_text)
        resume_profile = build_evidence_profile(resume_text)
        overlap_unit, matched, missing, negated_on_job = evidence_weighted_overlap(
            resume_profile,
            job_skills,
        )
        skill_score = overlap_unit * config.score_scale

        if job_skills:
            semantic_w = config.semantic_weight
            tfidf_w = config.tfidf_weight
            skill_w = config.skill_weight
            mix_note = (
                f"hybrid {semantic_w:.2f}*semantic + {tfidf_w:.2f}*tfidf + "
                f"{skill_w:.2f}*evidence_skill"
            )
        else:
            rest = config.semantic_weight + config.tfidf_weight
            if rest <= 0:
                semantic_w, tfidf_w = 0.5, 0.5
            else:
                semantic_w = config.semantic_weight / rest
                tfidf_w = config.tfidf_weight / rest
            skill_w = 0.0
            mix_note = (
                "job text has no catalog skills; skill channel skipped "
                f"({semantic_w:.2f}*semantic + {tfidf_w:.2f}*tfidf)"
            )

        overall = semantic_w * semantic_score + tfidf_w * tfidf_score + skill_w * skill_score
        stuffing_note = "stuffing_penalty=none"
        if resume_profile.stuffing_likely:
            overall *= STUFFING_OVERALL_FACTOR
            stuffing_note = f"stuffing_penalty=x{STUFFING_OVERALL_FACTOR:.2f}"

        evidence = (
            f"{HYBRID_MATCHER_NAME}: {mix_note}",
            f"semantic_score={semantic_score:.1f}/{config.score_scale:.0f}",
            f"tfidf_score={tfidf_score:.1f}/{config.score_scale:.0f}",
            f"skill_overlap_score={skill_score:.1f}/{config.score_scale:.0f} "
            f"({len(matched)}/{len(job_skills)} weighted job catalog skills)",
            (
                f"negated_skills={list(resume_profile.negated_skills)}; "
                f"weak_evidence_skills={list(resume_profile.weak_evidence_skills)}; "
                f"stuffing_likely={resume_profile.stuffing_likely}; {stuffing_note}"
            ),
            (
                f"negated_job_skills_ignored={list(negated_on_job)}"
                if negated_on_job
                else "negated_job_skills_ignored=[]"
            ),
            "Not a hiring probability.",
        )
        return MatchResult(
            overall_score=_clip_score(overall, config.score_scale),
            tfidf_similarity=_clip_score(tfidf_score, config.score_scale),
            skill_overlap_score=_clip_score(skill_score, config.score_scale),
            matched_skills=matched,
            missing_skills=missing,
            resume_skills=resume_profile.positive_skills + resume_profile.negated_skills,
            job_skills=job_skills,
            evidence=evidence,
            semantic_similarity=_clip_score(semantic_score, config.score_scale),
        )
