"""Rewrite provider implementations."""

from __future__ import annotations

from career_match.parsing.text import normalize_text
from career_match.tailoring.evidence_map import EvidenceMapResult
from career_match.tailoring.protocol import RewriteSuggestion, TailorSection


def _section_allowed(section: str, target: TailorSection) -> bool:
    if target == "all":
        return True
    return section == target


def _detect_section(resume_text: str, index: int) -> str:
    headers = {
        "summary": ("summary", "professional summary", "profile"),
        "experience": ("experience", "work experience", "employment"),
        "projects": ("projects", "selected projects"),
        "skills": ("skills", "technical skills", "skill set"),
    }
    prefix = resume_text[:index].lower()
    current = "experience"
    for section, markers in headers.items():
        for marker in markers:
            if marker in prefix:
                current = section
    return current


class DeterministicRewriteProvider:
    """Rule-based grounded rewrites from approved evidence only."""

    @property
    def name(self) -> str:
        return "deterministic"

    @property
    def available(self) -> bool:
        return True

    def generate_rewrites(
        self,
        *,
        resume_text: str,
        job_text: str,
        evidence_map: EvidenceMapResult,
        target: TailorSection,
    ) -> tuple[RewriteSuggestion, ...]:
        suggestions: list[RewriteSuggestion] = []

        for entry in evidence_map.requirements:
            if entry.status == "equivalent" and entry.supporting_text:
                section = _detect_section(resume_text, resume_text.lower().find(
                    entry.supporting_text[:20].lower()
                ) if entry.supporting_text else 0)
                if not _section_allowed(section, target):
                    continue
                introduced = (entry.requirement,)
                suggested = _introduce_terminology(
                    entry.supporting_text,
                    entry.requirement,
                )
                suggestions.append(
                    RewriteSuggestion(
                        section=section,
                        original_text=entry.supporting_text,
                        suggested_text=suggested,
                        keywords_introduced=introduced,
                        support_reason=entry.support_reason,
                        support_level="high",
                    )
                )
            elif entry.status == "partial" and entry.supporting_text:
                section = "skills"
                if not _section_allowed(section, target) and not _section_allowed(
                    "experience", target
                ):
                    continue
                suggested = _strengthen_partial_bullet(entry.supporting_text, entry.requirement)
                suggestions.append(
                    RewriteSuggestion(
                        section="experience",
                        original_text=entry.supporting_text,
                        suggested_text=suggested,
                        keywords_introduced=(),
                        support_reason=(
                            "Reframe listed skill as experience bullet using "
                            "existing resume facts only."
                        ),
                        support_level="medium",
                    )
                )

        return tuple(suggestions)


def _introduce_terminology(supporting_text: str, requirement: str) -> str:
    cleaned = normalize_text(supporting_text)
    label = requirement.upper() if "/" in requirement else requirement.title()
    if label.lower() in cleaned.lower():
        return cleaned
    return f"{cleaned} ({label})"


def _strengthen_partial_bullet(supporting_text: str, requirement: str) -> str:
    skill_label = requirement.replace("_", " ")
    return (
        f"Applied {skill_label} in project delivery settings — {normalize_text(supporting_text)}"
    )


class FakeRewriteProvider:
    """Test double with predictable output."""

    def __init__(self, suggestions: tuple[RewriteSuggestion, ...] | None = None) -> None:
        self._suggestions = suggestions or ()

    @property
    def name(self) -> str:
        return "fake-test-provider"

    @property
    def available(self) -> bool:
        return True

    def generate_rewrites(
        self,
        *,
        resume_text: str,
        job_text: str,
        evidence_map: EvidenceMapResult,
        target: TailorSection,
    ) -> tuple[RewriteSuggestion, ...]:
        return self._suggestions


class UnavailableLLMRewriteProvider:
    """Placeholder when no external LLM provider is configured."""

    @property
    def name(self) -> str:
        return "llm-unavailable"

    @property
    def available(self) -> bool:
        return False

    def generate_rewrites(
        self,
        *,
        resume_text: str,
        job_text: str,
        evidence_map: EvidenceMapResult,
        target: TailorSection,
    ) -> tuple[RewriteSuggestion, ...]:
        return ()


class OptionalLLMRewriteProvider:
    """Optional LLM phrasing layer; only rewrites pre-approved evidence entries."""

    def __init__(self) -> None:
        self._inner = self._build_inner()

    def _build_inner(self) -> UnavailableLLMRewriteProvider | None:
        import os

        if not os.environ.get("CAREER_MATCH_LLM_API_KEY", "").strip():
            return None
        # Provider-specific integration can be added behind this gate without
        # changing the tailoring service contract.
        return None

    @property
    def name(self) -> str:
        return "optional-llm"

    @property
    def available(self) -> bool:
        return self._inner is not None and self._inner.available

    def generate_rewrites(
        self,
        *,
        resume_text: str,
        job_text: str,
        evidence_map: EvidenceMapResult,
        target: TailorSection,
    ) -> tuple[RewriteSuggestion, ...]:
        if self._inner is None:
            return ()
        return self._inner.generate_rewrites(
            resume_text=resume_text,
            job_text=job_text,
            evidence_map=evidence_map,
            target=target,
        )
