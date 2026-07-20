"""Persona agents for the ACH roundtable, backed by a local Ollama model."""

from __future__ import annotations

import os

# httpx (used internally by the ollama client) honors the system HTTP proxy by
# default. On this machine a local proxy is configured that refuses to proxy
# loopback addresses, which turns every request to Ollama into a 502. Excluding
# localhost from proxying must happen before httpx reads the environment.
os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost")
os.environ.setdefault("no_proxy", "127.0.0.1,localhost")

from typing import Callable, List

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.ollama import OllamaChatCompletionClient

from ach_matrix import ACHMatrix, RATING_WEIGHTS

OLLAMA_MODEL = "gemma4"

# gemma4 isn't in autogen-ext's built-in model registry, so its capabilities
# (confirmed via `ollama show gemma4`: tools, vision, completion) must be
# declared explicitly.
OLLAMA_MODEL_INFO = ModelInfo(
    vision=True,
    function_calling=True,
    json_output=True,
    family=ModelFamily.UNKNOWN,
    structured_output=True,
)

RATING_HELP = ", ".join(f"'{r}'" for r in RATING_WEIGHTS)

PERSONAS: List[tuple[str, str]] = [
    (
        "DomainExpert",
        "You are a domain expert taking part in an Analysis of Competing "
        "Hypotheses (ACH) roundtable. Propose plausible hypotheses grounded "
        "in real-world knowledge and mechanisms, and contribute concrete, "
        "specific evidence relevant to the problem using your tools.",
    ),
    (
        "Skeptic",
        "You are the skeptic and devil's advocate in an ACH roundtable. "
        "Your job is to challenge every hypothesis and actively hunt for "
        "evidence that CONTRADICTS each one, not just evidence that "
        "confirms one. Flag unsupported assumptions and weak hypotheses.",
    ),
    (
        "EvidenceAnalyst",
        "You are the evidence analyst in an ACH roundtable. Gather and "
        "organize evidence relevant to the problem, and use view_matrix to "
        "check whether every hypothesis has been considered against every "
        "piece of evidence before the group moves to scoring.",
    ),
    (
        "QuantReviewer",
        "You are the quantitative reviewer in an ACH roundtable. Push for "
        "rigorous, consistent scoring criteria, catch contradictory or "
        "sloppy hypotheses/evidence, and keep the group on track toward a "
        "complete matrix.",
    ),
]


def make_model_client() -> OllamaChatCompletionClient:
    return OllamaChatCompletionClient(model=OLLAMA_MODEL, model_info=OLLAMA_MODEL_INFO)


def build_tools(matrix: ACHMatrix, scorer_name: str) -> List[Callable]:
    def add_hypothesis(name: str, description: str = "") -> str:
        """Propose a new hypothesis to explain the problem. Returns its id, e.g. 'H1'."""
        return matrix.add_hypothesis(name, description)

    def add_evidence(text: str, source: str = "") -> str:
        """Add a piece of evidence or argument relevant to the problem. Returns its id, e.g. 'E1'."""
        return matrix.add_evidence(text, source)

    def score_evidence(hypothesis_id: str, evidence_id: str, rating: str, rationale: str) -> str:
        f"""Score how consistent one piece of evidence is with one hypothesis.

        rating must be exactly one of: {RATING_HELP}.
        """
        return matrix.score_evidence(hypothesis_id, evidence_id, rating, rationale, scorer_name)

    def view_matrix() -> str:
        """View the current ACH matrix (hypotheses, evidence, scores so far) as a markdown table."""
        return matrix.render_markdown()

    return [add_hypothesis, add_evidence, score_evidence, view_matrix]


def build_personas(matrix: ACHMatrix, max_tool_iterations: int = 1) -> List[AssistantAgent]:
    agents = []
    for name, system_message in PERSONAS:
        agents.append(
            AssistantAgent(
                name=name,
                model_client=make_model_client(),
                tools=build_tools(matrix, scorer_name=name),
                system_message=system_message,
                reflect_on_tool_use=True,
                max_tool_iterations=max_tool_iterations,
            )
        )
    return agents
