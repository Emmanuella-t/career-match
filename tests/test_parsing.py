"""Text parsing tests."""

from career_match.parsing.text import normalize_text, repair_mojibake


def test_normalize_collapses_whitespace() -> None:
    assert normalize_text("Python\n\n  pandas\tSQL") == "Python pandas SQL"


def test_normalize_strips() -> None:
    assert normalize_text("  Java  ") == "Java"


def test_normalize_empty() -> None:
    assert normalize_text("") == ""
    assert normalize_text("   \n") == ""


def test_normalize_preserves_words() -> None:
    assert "scikit-learn" in normalize_text("Used scikit-learn for classification.")


def test_normalize_repairs_common_mojibake() -> None:
    repaired = repair_mojibake("NaÃ¯ve Bayes")
    assert repaired == "Naïve Bayes"
    assert "Naïve" in normalize_text("NaÃ¯ve Bayes classifier")


def test_repair_a_circumflex_punctuation_mojibake() -> None:
    # UTF-8 bullet (U+2022) decoded as Latin-1 becomes â\x80¢.
    mojibake = "Skills â\x80¢ Python"
    assert repair_mojibake(mojibake) == "Skills • Python"
    assert "•" in normalize_text(mojibake)


def test_repair_leaves_legitimate_chateau_unchanged() -> None:
    original = "Visited château during internships."
    assert repair_mojibake(original) == original
    assert "château" in normalize_text(original)
