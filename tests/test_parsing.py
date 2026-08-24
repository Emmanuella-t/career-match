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
