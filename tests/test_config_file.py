"""Tests for config file loading and ignore patterns functionality."""

import json
import os
import tempfile

import pytest

from intelephense_watcher.config.config_file import get_ignore_patterns, load_config_file
from intelephense_watcher.diagnostics import filter_by_ignore_patterns


class TestLoadConfigFile:
    """Tests for load_config_file function."""

    def test_loads_valid_config(self) -> None:
        """Test loading a valid intelephense.json config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "intelephense.json")
            config_data = {"ignore": ["vendor/**", "tests/fixtures/**"]}
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f)

            result = load_config_file(tmpdir)

            assert result is not None
            assert result == config_data

    def test_returns_none_for_missing_file(self) -> None:
        """Test that missing config file returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = load_config_file(tmpdir)
            assert result is None

    def test_returns_none_for_invalid_json(self) -> None:
        """Test that invalid JSON returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "intelephense.json")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("{ invalid json }")

            result = load_config_file(tmpdir)
            assert result is None

    def test_returns_none_for_directory_instead_of_file(self) -> None:
        """Test that a directory named intelephense.json returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "intelephense.json")
            os.makedirs(config_path)

            result = load_config_file(tmpdir)
            assert result is None

    def test_loads_empty_config(self) -> None:
        """Test loading an empty but valid JSON config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "intelephense.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

            result = load_config_file(tmpdir)

            assert result is not None
            assert result == {}


class TestGetIgnorePatterns:
    """Tests for get_ignore_patterns function."""

    def test_extracts_patterns_from_config(self) -> None:
        """Test extracting ignore patterns from valid config."""
        config = {"ignore": ["vendor/**", "*.generated.php"]}
        result = get_ignore_patterns(config)
        assert result == ["vendor/**", "*.generated.php"]

    def test_returns_empty_list_for_none_config(self) -> None:
        """Test that None config returns empty list."""
        result = get_ignore_patterns(None)
        assert result == []

    def test_returns_empty_list_for_missing_ignore_key(self) -> None:
        """Test that config without 'ignore' key returns empty list."""
        config = {"other_key": "value"}
        result = get_ignore_patterns(config)
        assert result == []

    def test_returns_empty_list_for_non_list_ignore(self) -> None:
        """Test that non-list 'ignore' value returns empty list."""
        config = {"ignore": "not-a-list"}
        result = get_ignore_patterns(config)
        assert result == []

    def test_filters_non_string_patterns(self) -> None:
        """Test that non-string patterns are filtered out."""
        config = {"ignore": ["valid/**", 123, None, {"key": "value"}, "also-valid"]}
        result = get_ignore_patterns(config)
        assert result == ["valid/**", "also-valid"]

    def test_returns_empty_list_for_empty_ignore_array(self) -> None:
        """Test that empty ignore array returns empty list."""
        config = {"ignore": []}
        result = get_ignore_patterns(config)
        assert result == []


class TestFilterByIgnorePatterns:
    """Tests for filter_by_ignore_patterns function."""

    def test_filters_matching_files(self) -> None:
        """Test that files matching patterns are filtered out."""
        diagnostics = {
            "file:///project/src/main.php": [{"severity": 1, "message": "Error"}],
            "file:///project/vendor/lib.php": [{"severity": 1, "message": "Error"}],
        }
        patterns = ["vendor/**"]
        workspace = "/project"

        result = filter_by_ignore_patterns(diagnostics, patterns, workspace)

        assert "file:///project/src/main.php" in result
        assert "file:///project/vendor/lib.php" not in result

    def test_no_filter_with_empty_patterns(self) -> None:
        """Test that empty patterns returns diagnostics unchanged."""
        diagnostics = {
            "file:///project/src/main.php": [{"severity": 1, "message": "Error"}],
        }

        result = filter_by_ignore_patterns(diagnostics, [], "/project")

        assert result == diagnostics

    def test_filters_nested_paths(self) -> None:
        """Test filtering deeply nested paths."""
        diagnostics = {
            "file:///project/tests/fixtures/sample.php": [{"severity": 1, "message": "Error"}],
            "file:///project/tests/unit/test.php": [{"severity": 1, "message": "Error"}],
        }
        patterns = ["tests/fixtures/**"]
        workspace = "/project"

        result = filter_by_ignore_patterns(diagnostics, patterns, workspace)

        assert "file:///project/tests/fixtures/sample.php" not in result
        assert "file:///project/tests/unit/test.php" in result

    def test_filters_by_extension(self) -> None:
        """Test filtering by file extension pattern."""
        diagnostics = {
            "file:///project/src/generated.php": [{"severity": 1, "message": "Error"}],
            "file:///project/src/main.php": [{"severity": 1, "message": "Error"}],
        }
        patterns = ["*.generated.php"]
        workspace = "/project"

        result = filter_by_ignore_patterns(diagnostics, patterns, workspace)

        # Note: *.generated.php pattern matches only at the root level
        # For nested files, src/generated.php doesn't match *.generated.php
        # but it would match **/*.generated.php
        assert len(result) == 2  # Both should remain with this pattern

    def test_filters_with_double_star_extension(self) -> None:
        """Test filtering with **/*.extension pattern."""
        diagnostics = {
            "file:///project/src/file.generated.php": [{"severity": 1, "message": "Error"}],
            "file:///project/src/main.php": [{"severity": 1, "message": "Error"}],
        }
        patterns = ["**/*.generated.php"]
        workspace = "/project"

        result = filter_by_ignore_patterns(diagnostics, patterns, workspace)

        assert "file:///project/src/file.generated.php" not in result
        assert "file:///project/src/main.php" in result

    def test_multiple_patterns(self) -> None:
        """Test filtering with multiple patterns."""
        diagnostics = {
            "file:///project/vendor/lib.php": [{"severity": 1, "message": "Error"}],
            "file:///project/tests/fixtures/sample.php": [{"severity": 1, "message": "Error"}],
            "file:///project/src/main.php": [{"severity": 1, "message": "Error"}],
        }
        patterns = ["vendor/**", "tests/fixtures/**"]
        workspace = "/project"

        result = filter_by_ignore_patterns(diagnostics, patterns, workspace)

        assert "file:///project/vendor/lib.php" not in result
        assert "file:///project/tests/fixtures/sample.php" not in result
        assert "file:///project/src/main.php" in result

    def test_empty_diagnostics(self) -> None:
        """Test with empty diagnostics dictionary."""
        result = filter_by_ignore_patterns({}, ["vendor/**"], "/project")
        assert result == {}

    def test_handles_backslash_in_path(self) -> None:
        """Test that Windows backslashes are handled correctly."""
        # Simulate Windows-style URI (though real URIs use forward slashes)
        diagnostics = {
            "file:///C:/project/vendor/lib.php": [{"severity": 1, "message": "Error"}],
            "file:///C:/project/src/main.php": [{"severity": 1, "message": "Error"}],
        }
        patterns = ["vendor/**"]
        workspace = "C:\\project"

        result = filter_by_ignore_patterns(diagnostics, patterns, workspace)

        assert "file:///C:/project/vendor/lib.php" not in result
        assert "file:///C:/project/src/main.php" in result

    def test_no_match_returns_all(self) -> None:
        """Test that non-matching patterns return all diagnostics."""
        diagnostics = {
            "file:///project/src/main.php": [{"severity": 1, "message": "Error"}],
            "file:///project/lib/util.php": [{"severity": 1, "message": "Error"}],
        }
        patterns = ["vendor/**", "tests/**"]
        workspace = "/project"

        result = filter_by_ignore_patterns(diagnostics, patterns, workspace)

        assert len(result) == 2
