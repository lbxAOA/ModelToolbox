"""Analysis of Competing Hypotheses (ACH) matrix, per Richards Heuer's method.

Shared mutable state that persona agents read/write via tool calls during
the AutoGen roundtable (see agents.py / main.py).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

RATING_WEIGHTS: Dict[str, int] = {
    "++": 2,   # very consistent
    "+": 1,    # consistent
    "0": 0,    # neutral / not applicable
    "-": -1,   # inconsistent
    "--": -2,  # very inconsistent
}

# Smaller local models often spell ratings out in English instead of using the
# terse ACH codes above; accept the common variants rather than erroring.
RATING_ALIASES: Dict[str, str] = {
    "very consistent": "++",
    "highly consistent": "++",
    "strongly consistent": "++",
    "consistent": "+",
    "somewhat consistent": "+",
    "weakly consistent": "+",
    "neutral": "0",
    "not applicable": "0",
    "n/a": "0",
    "na": "0",
    "irrelevant": "0",
    "inconsistent": "-",
    "somewhat inconsistent": "-",
    "weakly inconsistent": "-",
    "very inconsistent": "--",
    "highly inconsistent": "--",
    "strongly inconsistent": "--",
}


@dataclass
class Hypothesis:
    id: str
    name: str
    description: str = ""


@dataclass
class Evidence:
    id: str
    text: str
    source: str = ""


@dataclass
class Score:
    rating: str
    rationale: str
    scorer: str


class ACHMatrix:
    """Hypotheses x evidence consistency matrix.

    Ranking follows Heuer's core insight: the best-supported hypothesis is
    the one with the LEAST total inconsistency, not the one with the
    highest raw consistency total, since disconfirming evidence is more
    diagnostic than confirming evidence.
    """

    def __init__(self, max_hypotheses: int = 5, max_evidence: int = 8) -> None:
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.scores: Dict[Tuple[str, str], List[Score]] = {}
        self._h_counter = 0
        self._e_counter = 0
        self.max_hypotheses = max_hypotheses
        self.max_evidence = max_evidence

    def add_hypothesis(self, name: str, description: str = "") -> str:
        if len(self.hypotheses) >= self.max_hypotheses:
            return (
                f"error: hypothesis limit ({self.max_hypotheses}) reached, "
                "do not add more -- move on to evidence or scoring"
            )
        self._h_counter += 1
        hid = f"H{self._h_counter}"
        self.hypotheses[hid] = Hypothesis(hid, name, description)
        return hid

    def add_evidence(self, text: str, source: str = "") -> str:
        if len(self.evidence) >= self.max_evidence:
            return (
                f"error: evidence limit ({self.max_evidence}) reached, "
                "do not add more -- move on to scoring"
            )
        self._e_counter += 1
        eid = f"E{self._e_counter}"
        self.evidence[eid] = Evidence(eid, text, source)
        return eid

    def score_evidence(
        self, hypothesis_id: str, evidence_id: str, rating: str, rationale: str, scorer: str
    ) -> str:
        resolved_hid = self._resolve_id(hypothesis_id, self.hypotheses)
        if resolved_hid is None:
            return f"error: unknown hypothesis id {hypothesis_id!r}"
        resolved_eid = self._resolve_id(evidence_id, self.evidence)
        if resolved_eid is None:
            return f"error: unknown evidence id {evidence_id!r}"
        resolved_rating = self._normalize_rating(rating)
        if resolved_rating is None:
            return f"error: rating must be one of {list(RATING_WEIGHTS)}, got {rating!r}"
        key = (resolved_hid, resolved_eid)
        self.scores.setdefault(key, []).append(Score(resolved_rating, rationale, scorer))
        return f"recorded {scorer}: {resolved_hid}/{resolved_eid} = {resolved_rating}"

    @staticmethod
    def _resolve_id(raw: str, valid: Dict[str, object]) -> Optional[str]:
        """Models sometimes pass 'H1: Office network...' instead of 'H1'; be lenient."""
        raw = raw.strip()
        if raw in valid:
            return raw
        prefix = raw.split(":")[0].strip()
        if prefix in valid:
            return prefix
        match = re.match(r"^([HE]\d+)\b", raw)
        if match and match.group(1) in valid:
            return match.group(1)
        return None

    @staticmethod
    def _normalize_rating(raw: str) -> Optional[str]:
        """Models sometimes spell out ratings instead of using the '++'/'+'/'0'/'-'/'--' codes."""
        key = raw.strip().lower().strip(".")
        if key in RATING_WEIGHTS:
            return key
        return RATING_ALIASES.get(key)

    def unscored_pairs(self, scorer: Optional[str] = None) -> List[Tuple[str, str]]:
        """Pairs with no score yet (or none from `scorer` specifically)."""
        pairs = []
        for hid in self.hypotheses:
            for eid in self.evidence:
                existing = self.scores.get((hid, eid), [])
                if scorer is None:
                    if not existing:
                        pairs.append((hid, eid))
                elif not any(s.scorer == scorer for s in existing):
                    pairs.append((hid, eid))
        return pairs

    def _avg_weight(self, hid: str, eid: str) -> Optional[float]:
        scores = self.scores.get((hid, eid))
        if not scores:
            return None
        return sum(RATING_WEIGHTS[s.rating] for s in scores) / len(scores)

    def tally(self) -> List[Tuple[str, float, float]]:
        """(hypothesis_id, net_score, inconsistency_total), ranked best-first."""
        results = []
        for hid in self.hypotheses:
            net = 0.0
            inconsistency = 0.0
            for eid in self.evidence:
                w = self._avg_weight(hid, eid)
                if w is None:
                    continue
                net += w
                if w < 0:
                    inconsistency += -w
            results.append((hid, net, inconsistency))
        results.sort(key=lambda r: (r[2], -r[1]))
        return results

    @staticmethod
    def _weight_to_symbol(w: float) -> str:
        if w >= 1.5:
            return "++"
        if w >= 0.5:
            return "+"
        if w <= -1.5:
            return "--"
        if w <= -0.5:
            return "-"
        return "0"

    def render_markdown(self) -> str:
        if not self.hypotheses:
            return "_no hypotheses yet_"
        if not self.evidence:
            return "_no evidence yet_"

        h_ids = list(self.hypotheses)
        header = "| Evidence | " + " | ".join(
            f"{hid}: {self.hypotheses[hid].name}" for hid in h_ids
        ) + " |"
        sep = "|---" * (len(h_ids) + 1) + "|"
        rows = [header, sep]
        for eid, ev in self.evidence.items():
            cells = []
            for hid in h_ids:
                w = self._avg_weight(hid, eid)
                cells.append("·" if w is None else self._weight_to_symbol(w))
            rows.append(f"| {eid}: {ev.text[:60]} | " + " | ".join(cells) + " |")

        rows.append("")
        rows.append("**Tally (ranked best hypothesis first, by least inconsistency):**")
        rows.append("")
        rows.append("| Rank | Hypothesis | Net score | Inconsistency |")
        rows.append("|---|---|---|---|")
        for i, (hid, net, inc) in enumerate(self.tally(), 1):
            rows.append(f"| {i} | {hid}: {self.hypotheses[hid].name} | {net:+.1f} | {inc:.1f} |")
        return "\n".join(rows)
