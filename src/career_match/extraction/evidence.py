"""Deterministic skill evidence and negation heuristics for Hybrid Matcher v0.1.

These rules are transparent and inspectable. They are not NER, not an LLM,
and not a claim of perfect skill understanding.
"""

from __future__ import annotations

from dataclasses import dataclass

from career_match.extraction.skills import SKILL_LEXICON, _token_pattern
from career_match.parsing.text import normalize_text

# Phrases that weaken or negate a nearby skill mention. Checked in a short
# window before the skill hit.
NEGATION_PHRASES: tuple[str, ...] = (
    "no production",
    "no experience",
    "no practical",
    "have not",
    "has not",
    "had not",
    "have never",
    "has never",
    "never used",
    "never deployed",
    "not used",
    "not deployed",
    "limited exposure",
    "limited experience",
    "coursework only",
    "theoretical knowledge",
    "theoretical only",
    "familiar with but",
    "familiar but not",
    "without production",
    "without practical",
    "not owned",
    "does not own",
    "do not own",
)

SKILLS_SECTION_MARKERS: tuple[str, ...] = (
    "skills:",
    "skill set:",
    "technical skills:",
)

# When a resume lists this many distinct catalog skills, treat the skill
# channel as keyword-stuffing-prone and apply a documented discount.
STUFFING_SKILL_COUNT = 16

NEGATION_WINDOW_CHARS = 70
KEYWORD_LIST_WEIGHT = 0.45
NEGATED_WEIGHT = 0.0
EXPERIENCE_WEIGHT = 1.0
STUFFING_SKILL_CHANNEL_FACTOR = 0.25
# Extra overall multiplier when a resume looks keyword-stuffed. Transparent and
# applied after the weighted mix so stuffing cannot dominate on catalog density.
STUFFING_OVERALL_FACTOR = 0.72


@dataclass(frozen=True)
class SkillEvidence:
    """One catalog skill with a transparent evidence label."""

    name: str
    start: int
    end: int
    evidence: str  # "experience" | "keyword_list" | "negated"
    weight: float


@dataclass(frozen=True)
class EvidenceSkillProfile:
    """Aggregated resume skill evidence used by the hybrid skill channel."""

    positive_skills: tuple[str, ...]
    negated_skills: tuple[str, ...]
    weak_evidence_skills: tuple[str, ...]
    skill_weights: dict[str, float]
    stuffing_likely: bool
    skill_channel_factor: float


def _skills_section_start(normalized: str) -> int | None:
    for marker in SKILLS_SECTION_MARKERS:
        index = normalized.find(marker)
        if index >= 0:
            return index
    return None


def _is_negated(normalized_lower: str, start: int, end: int) -> bool:
    """True when a negation phrase appears in the same sentence before the skill."""
    left = max(0, start - NEGATION_WINDOW_CHARS)
    prefix = normalized_lower[left:start]
    # Keep the window inside the current sentence.
    boundary = max(prefix.rfind(". "), prefix.rfind("! "), prefix.rfind("? "))
    if boundary >= 0:
        left = left + boundary + 2
    window = normalized_lower[left:end]
    return any(phrase in window for phrase in NEGATION_PHRASES)


def _find_all_hits(normalized: str, surfaces: tuple[str, ...]) -> list[tuple[int, int]]:
    hits: list[tuple[int, int]] = []
    for surface in surfaces:
        pattern = _token_pattern(surface)
        for match in pattern.finditer(normalized):
            hits.append((match.start(), match.end()))
    hits.sort(key=lambda item: item[0])
    return hits


def classify_skill_mentions(text: str) -> tuple[SkillEvidence, ...]:
    """Classify each catalog skill that appears in ``text``.

    Preference order per skill:
    1. negated mention in the narrative (before Skills:) → negated (0.0),
       even if the same skill is repeated in a keyword list
    2. non-negated mention before a Skills: section → experience (1.0)
    3. non-negated mention only inside Skills: → keyword_list (0.45)
    """
    normalized = normalize_text(text)
    if not normalized:
        return ()

    lowered = normalized.lower()
    section_start = _skills_section_start(lowered)
    found: list[SkillEvidence] = []
    for canonical, surfaces in SKILL_LEXICON.items():
        hits = _find_all_hits(normalized, surfaces)
        if not hits:
            continue

        experience_hit: tuple[int, int] | None = None
        keyword_hit: tuple[int, int] | None = None
        negated_hit: tuple[int, int] | None = None
        for start, end in hits:
            in_skills_section = section_start is not None and start >= section_start
            if _is_negated(lowered, start, end):
                # Narrative negation wins over a later Skills: list entry.
                if not in_skills_section and negated_hit is None:
                    negated_hit = (start, end)
                continue
            if in_skills_section:
                if keyword_hit is None:
                    keyword_hit = (start, end)
            elif experience_hit is None:
                experience_hit = (start, end)

        if negated_hit is not None and experience_hit is None:
            start, end = negated_hit
            evidence, weight = "negated", NEGATED_WEIGHT
        elif experience_hit is not None:
            start, end = experience_hit
            evidence, weight = "experience", EXPERIENCE_WEIGHT
        elif keyword_hit is not None:
            start, end = keyword_hit
            evidence, weight = "keyword_list", KEYWORD_LIST_WEIGHT
        else:
            continue

        found.append(
            SkillEvidence(
                name=canonical,
                start=start,
                end=end,
                evidence=evidence,
                weight=weight,
            )
        )
    found.sort(key=lambda item: item.start)
    return tuple(found)


def build_evidence_profile(text: str) -> EvidenceSkillProfile:
    """Aggregate per-skill evidence for hybrid skill coverage."""
    mentions = classify_skill_mentions(text)
    weights = {item.name: item.weight for item in mentions}
    positive = tuple(item.name for item in mentions if item.weight > 0)
    negated = tuple(item.name for item in mentions if item.evidence == "negated")
    weak = tuple(item.name for item in mentions if item.evidence == "keyword_list")
    stuffing_likely = len(mentions) >= STUFFING_SKILL_COUNT
    factor = STUFFING_SKILL_CHANNEL_FACTOR if stuffing_likely else 1.0
    return EvidenceSkillProfile(
        positive_skills=positive,
        negated_skills=negated,
        weak_evidence_skills=weak,
        skill_weights=weights,
        stuffing_likely=stuffing_likely,
        skill_channel_factor=factor,
    )


def evidence_weighted_overlap(
    resume_profile: EvidenceSkillProfile,
    job_skills: tuple[str, ...],
) -> tuple[float, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Job-skill coverage using evidence weights.

    Returns ``(coverage in [0,1], matched, missing, negated_matched_on_job)``.
    Coverage averages per-job-skill evidence weights, then applies the
    stuffing channel factor when the resume looks keyword-stuffed.
    """
    if not job_skills:
        return 0.0, (), (), ()

    matched: list[str] = []
    missing: list[str] = []
    negated_on_job: list[str] = []
    total = 0.0
    for skill in job_skills:
        weight = resume_profile.skill_weights.get(skill, 0.0)
        total += weight
        if weight > 0:
            matched.append(skill)
        else:
            missing.append(skill)
            if skill in resume_profile.negated_skills:
                negated_on_job.append(skill)

    coverage = (total / len(job_skills)) * resume_profile.skill_channel_factor
    return coverage, tuple(matched), tuple(missing), tuple(negated_on_job)
