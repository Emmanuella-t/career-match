"""Tests for evidence-aware skill extraction and negation heuristics."""

from __future__ import annotations

from career_match.extraction.evidence import (
    KEYWORD_LIST_WEIGHT,
    build_evidence_profile,
    classify_skill_mentions,
    evidence_weighted_overlap,
)


def test_negated_docker_is_not_positive_evidence() -> None:
    text = (
        "Four years of FastAPI and SQL backends with Git. "
        "No production Docker experience. Have not deployed services to AWS. "
        "Skills: Python, FastAPI, Docker, Kubernetes, AWS, Git"
    )
    profile = build_evidence_profile(text)
    assert "docker" in profile.negated_skills
    assert "docker" not in profile.positive_skills
    assert profile.skill_weights.get("docker", 1.0) == 0.0


def test_limited_exposure_kubernetes_is_negated() -> None:
    text = (
        "Python deploy scripts on AWS. Limited exposure to Kubernetes. "
        "Skills: Python, Docker, AWS, Kubernetes, Git, Linux"
    )
    profile = build_evidence_profile(text)
    assert "kubernetes" in profile.negated_skills


def test_experience_mention_outranks_skills_section() -> None:
    text = (
        "Built Docker containers and FastAPI services on Linux with Git reviews.\n\n"
        "Skills: Docker, FastAPI, Git, Linux, React"
    )
    mentions = {item.name: item for item in classify_skill_mentions(text)}
    assert mentions["docker"].evidence == "experience"
    assert mentions["docker"].weight == 1.0
    assert mentions["react"].evidence == "keyword_list"
    assert mentions["react"].weight == KEYWORD_LIST_WEIGHT


def test_keyword_list_only_skill_has_weaker_weight() -> None:
    text = "Backend engineer focused on reliability.\n\nSkills: Python, Docker, Kubernetes"
    profile = build_evidence_profile(text)
    assert "python" in profile.weak_evidence_skills
    assert profile.skill_weights["python"] == KEYWORD_LIST_WEIGHT


def test_stuffing_triggers_channel_factor() -> None:
    skills = (
        "Python, Java, JavaScript, TypeScript, SQL, C++, React, Next.js, FastAPI, "
        "Django, PyTorch, TensorFlow, scikit-learn, pandas, NumPy, AWS, Azure, "
        "GCP, Docker, Kubernetes, Git, Linux, Machine Learning, Deep Learning, "
        "NLP, REST APIs, HTML, CSS"
    )
    text = f"Claims many tools without outcomes.\n\nSkills: {skills}"
    profile = build_evidence_profile(text)
    assert profile.stuffing_likely is True
    assert profile.skill_channel_factor < 1.0


def test_evidence_overlap_ignores_negated_job_skills() -> None:
    resume = (
        "API developer. No production Docker experience. "
        "Skills: Python, FastAPI, Docker, Git"
    )
    profile = build_evidence_profile(resume)
    coverage, matched, missing, negated = evidence_weighted_overlap(
        profile,
        ("python", "docker", "git"),
    )
    assert "docker" in negated
    assert "docker" in missing
    assert "python" in matched
    assert coverage < 1.0
