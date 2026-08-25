"""Skill extraction tests."""

from career_match.extraction.skills import extract_skills


def test_extract_known_skills() -> None:
    skills = extract_skills("Built APIs with Python, SQL, and Docker.")
    names = [skill.name for skill in skills]
    assert names == ["python", "sql", "docker"]


def test_extract_case_insensitive() -> None:
    names = [skill.name for skill in extract_skills("PYTHON and JavaScript")]
    assert names == ["python", "javascript"]


def test_extract_none() -> None:
    assert extract_skills("Enjoy hiking and community theater.") == ()


def test_extract_unique_order() -> None:
    names = [skill.name for skill in extract_skills("Python and python and PYTHON")]
    assert names == ["python"]


def test_extract_ignores_partial_tokens() -> None:
    names = [skill.name for skill in extract_skills("The javascripted demo used java.")]
    assert "javascript" not in names
    assert names == ["java"]


def test_skill_span_offsets() -> None:
    text = "Experience with pandas and numpy"
    skills = extract_skills(text)
    by_name = {skill.name: skill for skill in skills}
    assert text[by_name["pandas"].start : by_name["pandas"].end].lower() == "pandas"
    assert text[by_name["numpy"].start : by_name["numpy"].end].lower() == "numpy"
