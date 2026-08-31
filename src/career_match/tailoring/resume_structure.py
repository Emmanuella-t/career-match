"""Structured resume representation for grounded tailoring apply/export."""

from __future__ import annotations

import re
from dataclasses import dataclass

from career_match.tailoring.protocol import RewriteSuggestion

_SECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("summary", re.compile(r"^(summary|professional summary|profile)\s*$", re.I)),
    ("experience", re.compile(r"^(experience|work experience|employment)\s*$", re.I)),
    ("projects", re.compile(r"^(projects|selected projects)\s*$", re.I)),
    ("skills", re.compile(r"^(skills|technical skills|skill set)\s*$", re.I)),
    ("education", re.compile(r"^(education|academic background)\s*$", re.I)),
)


@dataclass(frozen=True, slots=True)
class SectionBlock:
    """One resume section block with change tracking."""

    section: str
    text: str
    change_status: str  # unchanged | accepted | rejected
    original_text: str | None = None
    suggestion_id: str | None = None


@dataclass(frozen=True, slots=True)
class StructuredResume:
    """Section-oriented resume used for preview and export."""

    header: str
    sections: tuple[SectionBlock, ...]

    def to_text(self) -> str:
        parts: list[str] = []
        if self.header.strip():
            parts.append(self.header.strip())
        for block in self.sections:
            if block.section != "header" and block.text.strip():
                title = block.section.replace("_", " ").title()
                if block.section in {"experience", "skills", "projects", "education", "summary"}:
                    parts.append(f"\n{title}\n{block.text.strip()}")
                else:
                    parts.append(block.text.strip())
        return "\n".join(parts).strip()


def _detect_section_heading(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    for name, pattern in _SECTION_PATTERNS:
        if pattern.match(stripped):
            return name
    return None


def parse_resume_sections(resume_text: str) -> StructuredResume:
    """Split resume text into structured sections preserving source content."""
    lines = resume_text.replace("\r\n", "\n").split("\n")
    header_lines: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_section = "experience"
    current_lines: list[str] = []
    seen_section = False

    for line in lines:
        heading = _detect_section_heading(line)
        if heading is not None:
            if current_lines or seen_section:
                sections.append((current_section, current_lines))
            current_section = heading
            current_lines = []
            seen_section = True
            continue
        if not seen_section:
            header_lines.append(line)
        else:
            current_lines.append(line)

    if current_lines or seen_section:
        sections.append((current_section, current_lines))
    elif header_lines:
        sections.append(("experience", header_lines))
        header_lines = []

    blocks = tuple(
        SectionBlock(
            section=name,
            text="\n".join(content).strip(),
            change_status="unchanged",
        )
        for name, content in sections
        if "\n".join(content).strip() or name == "skills"
    )
    if not blocks and resume_text.strip():
        blocks = (
            SectionBlock(section="experience", text=resume_text.strip(), change_status="unchanged"),
        )
    return StructuredResume(header="\n".join(header_lines).strip(), sections=blocks)


def apply_suggestions(
    structured: StructuredResume,
    accepted: tuple[tuple[str, RewriteSuggestion], ...],
) -> StructuredResume:
    """Apply accepted grounded suggestions within their sections."""
    updated_sections: list[SectionBlock] = []
    for block in structured.sections:
        text = block.text
        status = "unchanged"
        original: str | None = None
        applied_id: str | None = None

        for suggestion_id, suggestion in accepted:
            if suggestion.section != block.section:
                continue
            if suggestion.original_text not in text:
                continue
            text = text.replace(suggestion.original_text, suggestion.suggested_text, 1)
            status = "accepted"
            original = suggestion.original_text
            applied_id = suggestion_id
            break

        updated_sections.append(
            SectionBlock(
                section=block.section,
                text=text,
                change_status=status,
                original_text=original,
                suggestion_id=applied_id,
            )
        )

    return StructuredResume(header=structured.header, sections=tuple(updated_sections))
