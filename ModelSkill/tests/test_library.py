"""Tests for modeltoolbox_skill library module."""

import pytest
from pathlib import Path
from modeltoolbox_skill.library import (
    SkillRecord,
    slugify,
    parse_skill,
    discover_skills,
)


def test_slugify():
    """Test slugify function."""
    assert slugify("My Skill") == "my-skill"
    assert slugify("Test_Skill_123") == "test_skill_123"
    assert slugify("  spaces  ") == "spaces"
    assert slugify("Special!@#$%Characters") == "special-characters"


def test_slugify_invalid():
    """Test slugify with invalid input."""
    with pytest.raises(ValueError, match="must contain at least one safe character"):
        slugify("@#$%")
    # Both "." and ".." will raise "must contain at least one safe character" 
    # after stripping, not "Invalid skill name"
    with pytest.raises(ValueError):
        slugify(".")
    with pytest.raises(ValueError):
        slugify("..")


def test_skill_record_creation():
    """Test SkillRecord creation."""
    record = SkillRecord(
        name="test-skill",
        path="skills/test-skill/SKILL.md",
        description="A test skill",
        triggers=["test", "testing"],
    )
    assert record.name == "test-skill"
    assert record.path == "skills/test-skill/SKILL.md"
    assert "test" in record.triggers


def test_skill_record_immutable():
    """Test that SkillRecord is immutable."""
    record = SkillRecord(
        name="test",
        path="test.md",
        description="test",
        triggers=[],
    )
    with pytest.raises(AttributeError):
        record.name = "changed"  # type: ignore


def test_parse_skill_with_frontmatter(tmp_path):
    """Test parsing skill with YAML frontmatter."""
    skill_dir = tmp_path / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\n"
        "name: Test Skill\n"
        "description: A test skill for testing\n"
        "triggers: test, testing\n"
        "---\n"
        "# Test Skill\n"
        "This is a test skill.\n",
        encoding="utf-8",
    )
    
    record = parse_skill(skill_file, skills_dir=tmp_path / "skills")
    assert record is not None
    assert record.name == "Test Skill"
    assert record.description == "A test skill for testing"
    assert "test" in record.triggers
    assert "testing" in record.triggers


def test_parse_skill_without_frontmatter(tmp_path):
    """Test parsing skill without frontmatter."""
    skill_dir = tmp_path / "skills" / "simple-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "# Simple Skill\n"
        "This is a simple skill without frontmatter.\n",
        encoding="utf-8",
    )
    
    record = parse_skill(skill_file, skills_dir=tmp_path / "skills")
    assert record is not None
    assert record.name == "simple-skill"  # Uses directory name
    assert "Simple Skill" in record.description


def test_parse_skill_nonexistent(tmp_path):
    """Test parsing nonexistent skill file."""
    skill_file = tmp_path / "nonexistent" / "SKILL.md"
    record = parse_skill(skill_file, skills_dir=tmp_path)
    assert record is None


def test_discover_skills(tmp_path):
    """Test discovering multiple skills."""
    skills_dir = tmp_path / "skills"
    
    # Create first skill
    skill1_dir = skills_dir / "skill-one"
    skill1_dir.mkdir(parents=True)
    (skill1_dir / "SKILL.md").write_text("# Skill One\nFirst skill", encoding="utf-8")
    
    # Create second skill
    skill2_dir = skills_dir / "skill-two"
    skill2_dir.mkdir(parents=True)
    (skill2_dir / "SKILL.md").write_text("# Skill Two\nSecond skill", encoding="utf-8")
    
    records = discover_skills(skills_dir)
    assert len(records) == 2
    assert records[0].name == "skill-one"
    assert records[1].name == "skill-two"


def test_discover_skills_empty_dir(tmp_path):
    """Test discovering skills in empty directory."""
    skills_dir = tmp_path / "empty_skills"
    skills_dir.mkdir()
    records = discover_skills(skills_dir)
    assert len(records) == 0


def test_discover_skills_nonexistent_dir(tmp_path):
    """Test discovering skills in nonexistent directory."""
    skills_dir = tmp_path / "nonexistent"
    records = discover_skills(skills_dir)
    assert len(records) == 0
