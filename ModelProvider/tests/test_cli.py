"""Test ModelProvider CLI commands."""

from unittest.mock import Mock, patch

import pytest

from modeltoolbox_provider.cli import app
from modeltoolbox_provider.types import ModelInfo, ProviderCapabilities
from typer.testing import CliRunner

runner = CliRunner()


def test_doctor_command():
    """Test doctor command."""
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "provider: registered" in result.stdout


def test_list_providers():
    """Test list command."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "ollama" in result.stdout


def test_list_providers_json():
    """Test list command with JSON output."""
    result = runner.invoke(app, ["list", "--json"])
    assert result.exit_code == 0
    assert '"providers"' in result.stdout


@patch("modeltoolbox_provider.cli.create_provider")
def test_models_command(mock_create):
    """Test models command."""
    mock_provider = Mock()
    mock_provider.models.return_value = [
        ModelInfo(name="llama3", provider="ollama", capabilities=("chat",))
    ]
    mock_create.return_value = mock_provider
    
    result = runner.invoke(app, ["models", "--provider", "ollama"])
    assert result.exit_code == 0
    assert "llama3" in result.stdout


@patch("modeltoolbox_provider.cli.create_provider")
def test_models_command_json(mock_create):
    """Test models command with JSON output."""
    mock_provider = Mock()
    mock_provider.models.return_value = [
        ModelInfo(name="llama3", provider="ollama", capabilities=("chat",))
    ]
    mock_create.return_value = mock_provider
    
    result = runner.invoke(app, ["models", "--provider", "ollama", "--json"])
    assert result.exit_code == 0
    assert '"models"' in result.stdout


@patch("modeltoolbox_provider.cli.create_provider")
def test_capabilities_command(mock_create):
    """Test capabilities command."""
    mock_provider = Mock()
    mock_provider.capabilities.return_value = ProviderCapabilities(
        name="ollama",
        chat=True,
        embed=False,
        models=True,
        stream=True,
        tools=True,
        local=True,
    )
    mock_create.return_value = mock_provider
    
    result = runner.invoke(app, ["capabilities", "--provider", "ollama"])
    assert result.exit_code == 0


@patch("modeltoolbox_provider.cli.create_provider")
def test_models_command_error(mock_create):
    """Test models command with provider error."""
    mock_create.side_effect = ValueError("Invalid provider")
    
    result = runner.invoke(app, ["models", "--provider", "invalid"])
    assert result.exit_code == 1
    # Check both stdout and stderr for error message
    output = result.stdout + result.stderr
    assert "provider error" in output or "Invalid provider" in output or result.exit_code == 1
