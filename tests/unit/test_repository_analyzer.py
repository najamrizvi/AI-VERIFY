from pathlib import Path

import pytest

from ai_verify.repository.analyzer import RepositoryAnalyzer


def test_discovers_python_files(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("VALUE = 1")
    (tmp_path / "src" / "utils.py").write_text("VALUE = 2")
    (tmp_path / "README.md").write_text("# Test")

    result = RepositoryAnalyzer().analyze(tmp_path)

    assert [item.relative_path for item in result.python_files] == [
        "src/app.py",
        "src/utils.py",
    ]


def test_discovery_is_deterministic(tmp_path: Path):
    (tmp_path / "z.py").write_text("")
    (tmp_path / "a.py").write_text("")
    (tmp_path / "middle.py").write_text("")

    analyzer = RepositoryAnalyzer()

    first = analyzer.analyze(tmp_path)
    second = analyzer.analyze(tmp_path)

    assert first.python_files == second.python_files


def test_ignored_directories_are_not_scanned(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "__pycache__").mkdir()

    (tmp_path / "src" / "app.py").write_text("")
    (tmp_path / ".venv" / "ignored.py").write_text("")
    (tmp_path / "__pycache__" / "ignored.py").write_text("")

    result = RepositoryAnalyzer().analyze(tmp_path)

    assert [item.relative_path for item in result.python_files] == [
        "src/app.py",
    ]


def test_nonexistent_repository_is_rejected(tmp_path: Path):
    missing = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        RepositoryAnalyzer().analyze(missing)


def test_file_cannot_be_used_as_repository_root(tmp_path: Path):
    file_path = tmp_path / "repository.txt"
    file_path.write_text("not a repository")

    with pytest.raises(NotADirectoryError):
        RepositoryAnalyzer().analyze(file_path)


def test_discovered_paths_remain_inside_selected_root(tmp_path: Path):
    (tmp_path / "inside.py").write_text("")

    result = RepositoryAnalyzer().analyze(tmp_path)

    for item in result.python_files:
        assert item.absolute_path.is_relative_to(tmp_path.resolve())


def test_non_python_files_are_not_discovered(tmp_path: Path):
    (tmp_path / "README.md").write_text("")
    (tmp_path / "config.json").write_text("{}")
    (tmp_path / "app.py").write_text("")

    result = RepositoryAnalyzer().analyze(tmp_path)

    assert [item.relative_path for item in result.python_files] == [
        "app.py",
    ]
