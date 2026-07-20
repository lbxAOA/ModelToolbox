"""Shared ACH roundtable pipeline: discussion phase + independent scoring phase.

Importable by both a CLI front-end (which may print via autogen's Console)
and the MCP server front-end (which must keep stdout clean for JSON-RPC and
therefore drains message streams silently).
"""

from __future__ import annotations

import sys
from typing import Awaitable, Callable, Optional

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat

from ach_matrix import ACHMatrix
from agents import build_personas, make_model_client

READY_PHRASE = "MATRIX_READY"

DISCUSSION_PROMPT_TEMPLATE = """\
Problem to analyze: {problem}

As a roundtable, collaboratively build an Analysis of Competing Hypotheses
(ACH) matrix for this problem:

1. Propose AT MOST {hyp_soft_cap} distinct, mutually exclusive hypotheses
   using add_hypothesis (add_hypothesis will start rejecting calls after
   {hyp_cap} -- stop at {hyp_soft_cap} so the group has room to add one
   more only if truly needed).
2. Contribute AT MOST {ev_soft_cap} pieces of evidence/arguments using
   add_evidence (it will start rejecting calls after {ev_cap}), including
   evidence that might DISCONFIRM hypotheses, not just support them.
3. Use view_matrix at any time to check progress.
4. Do NOT score evidence yet -- scoring happens in a separate phase.

When the group agrees the hypothesis and evidence lists are complete and
diverse enough to proceed to scoring, have one agent say the single word
{ready_phrase} on its own line.
"""

SCORING_PROMPT_TEMPLATE = """\
Hypothesis {hid}: {hname}
Evidence {eid}: {etext}

Call score_evidence exactly once for this single pair:
  hypothesis_id="{hid}", evidence_id="{eid}", rating=<one of '++','+','0','-','--'>, rationale=<one sentence>

Use the bare id ({hid} / {eid}), not the full hypothesis/evidence text, and
use exactly one of the five rating codes, not a spelled-out word.
"""

StreamConsumer = Callable[[object], Awaitable[None]]


async def _drain(stream: object, consume: Optional[StreamConsumer]) -> None:
    if consume is not None:
        await consume(stream)
        return
    async for _ in stream:  # type: ignore[union-attr]
        pass


async def run_discussion(
    matrix: ACHMatrix, problem: str, consume: Optional[StreamConsumer] = None
) -> None:
    agents = build_personas(matrix)
    agent_names = [a.name for a in agents]
    termination = TextMentionTermination(READY_PHRASE, sources=agent_names) | MaxMessageTermination(40)
    team = SelectorGroupChat(
        agents,
        model_client=make_model_client(),
        termination_condition=termination,
    )
    prompt = DISCUSSION_PROMPT_TEMPLATE.format(
        problem=problem,
        ready_phrase=READY_PHRASE,
        hyp_soft_cap=max(matrix.max_hypotheses - 1, 1),
        hyp_cap=matrix.max_hypotheses,
        ev_soft_cap=max(matrix.max_evidence - 2, 1),
        ev_cap=matrix.max_evidence,
    )
    await _drain(team.run_stream(task=prompt), consume)


async def run_scoring(matrix: ACHMatrix, consume: Optional[StreamConsumer] = None) -> None:
    agents = build_personas(matrix, max_tool_iterations=2)
    for agent in agents:
        for hid, eid in matrix.unscored_pairs(scorer=agent.name):
            prompt = SCORING_PROMPT_TEMPLATE.format(
                hid=hid,
                hname=matrix.hypotheses[hid].name,
                eid=eid,
                etext=matrix.evidence[eid].text,
            )
            for _ in range(2):
                try:
                    await _drain(agent.run_stream(task=prompt), consume)
                except Exception as exc:  # local models occasionally emit an
                    # empty tool-reflection turn; skip and retry rather than
                    # aborting the whole scoring pass.
                    print(f"  [warn] {agent.name} on {hid}/{eid}: {exc!r}", file=sys.stderr)
                if any(s.scorer == agent.name for s in matrix.scores.get((hid, eid), [])):
                    break
        await agent.close()


async def run_ach_pipeline(
    problem: str,
    max_hypotheses: int = 5,
    max_evidence: int = 8,
    consume: Optional[StreamConsumer] = None,
) -> ACHMatrix:
    """Run the full discussion + scoring pipeline and return the populated matrix."""
    matrix = ACHMatrix(max_hypotheses=max_hypotheses, max_evidence=max_evidence)
    await run_discussion(matrix, problem, consume=consume)
    if matrix.hypotheses and matrix.evidence:
        await run_scoring(matrix, consume=consume)
    return matrix
