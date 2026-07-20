"""MCP server exposing the ACH (Analysis of Competing Hypotheses) multi-agent
roundtable as a single tool. Runs entirely on a local Ollama model (gemma4 by
default, see agents.py) -- no external API keys required.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from pipeline import run_ach_pipeline

mcp = FastMCP("ach-roundtable")


@mcp.tool()
async def run_ach_roundtable(problem: str, max_hypotheses: int = 5, max_evidence: int = 8) -> str:
    """Analyze a complex problem using a multi-agent Analysis of Competing
    Hypotheses (ACH) roundtable.

    Four persona agents (a domain expert, a skeptic/devil's-advocate, an
    evidence analyst, and a quantitative reviewer) discuss the problem to
    jointly propose hypotheses and evidence, then each independently scores
    every (hypothesis, evidence) pair for consistency. Hypotheses are ranked
    by LEAST total inconsistency (Heuer's method), not highest raw score,
    since disconfirming evidence is more diagnostic than confirming evidence.

    This can take several minutes depending on how many hypotheses/evidence
    the roundtable proposes and how fast the local model runs.

    Args:
        problem: The complex problem or question to analyze.
        max_hypotheses: Hard cap on distinct hypotheses (default 5).
        max_evidence: Hard cap on evidence/argument items (default 8).

    Returns:
        A markdown report: the full hypothesis x evidence consistency matrix
        plus a final ranking table, or a short message if the roundtable
        failed to produce a usable matrix.
    """
    matrix = await run_ach_pipeline(problem, max_hypotheses=max_hypotheses, max_evidence=max_evidence)
    if not matrix.hypotheses or not matrix.evidence:
        return "The roundtable discussion ended without producing a usable hypothesis/evidence set."
    return matrix.render_markdown()


if __name__ == "__main__":
    mcp.run()
