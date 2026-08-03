"""Test ModelSkill CLI commands."""

from unittest.mock import Mock, patch
import pytest
from pathlib import Path
from modeltoolbox_skill.cli import app
from modeltoolbox_skill.library import SkillRecord
from typer.testing import CliRunner

runner = CliRunner()


def test_doctor_command():
    """Test doctor command."""
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "skill: registered" in result.stdout


def test_list_command_no_skills(tmp_path):
    """Test list command with no skills."""
    with patch("modeltoolbox_skill.cli.discover_skills") as mock_discover:
        mock_discover.return_value = []
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0


def test_list_command_with_skills(tmp_path):
    """Test list command with skills."""
    mock_skills = [
        SkillRecord(
            name="test-skill",
            path="skills/test-skill/SKILL.md",
            description="A test skill",
            triggers=["test"],
        )
    ]
    with patch("modeltoolbox_skill.cli.discover_skills") as mock_discover:
        mock_discover.return_value = mock_skills
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "test-skill" in result.stdout


def test_list_command_json(tmp_path):
    """Test list command with JSON output."""
    mock_skills = [
        SkillRecord(
            name="test-skill",
            path="skills/test-skill/SKILL.md",
            description="A test skill",
            triggers=["test"],
        )
    ]
    with patch("modeltoolbox_skill.cli.discover_skills") as mock_discover:
        mock_discover.return_value = mock_skills
        result = runner.invoke(app, ["list", "--json"])
        assert result.exit_code == 0
        assert '"skills"' in result.stdout


def test_build_command(tmp_path):
    """Test build-registry command."""
    with patch("modeltoolbox_skill.cli.build_registry") as mock_build:
        mock_build.return_value = {"skill_count": 0, "skills": []}
        result = runner.invoke(app, ["build-registry"])
        assert result.exit_code == 0
        mock_build.assert_called_once()


def test_search_command(tmp_path):
    """Test search command."""
    mock_skills = [
        SkillRecord(
            name="test-skill",
            path="skills/test-skill/SKILL.md",
            description="A test skill",
            triggers=["test"],
        )
    ]
    with patch("modeltoolbox_skill.cli.search_skills") as mock_search:
        mock_search.return_value = mock_skills
        result = runner.invoke(app, ["search", "test"])
        assert result.exit_code == 0
        assert "test-skill" in result.stdout
