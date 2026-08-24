"""Package import and version tests."""

from career_match import MatchingNotImplementedError, __version__


def test_import_career_match() -> None:
    import career_match

    assert career_match.__name__ == "career_match"


def test_package_exposes_version() -> None:
    assert __version__ == "0.1.0"


def test_subpackages_importable() -> None:
    from career_match import data, evaluation, extraction, matching, parsing
    from career_match import core as core_pkg

    assert core_pkg.__name__.endswith("core")
    assert data.__name__.endswith("data")
    assert parsing.__name__.endswith("parsing")
    assert extraction.__name__.endswith("extraction")
    assert matching.__name__.endswith("matching")
    assert evaluation.__name__.endswith("evaluation")
    assert issubclass(MatchingNotImplementedError, Exception)
