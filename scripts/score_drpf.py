"""Score DRPF rates from a JSONL file of {ref, hyp} records.

Rates follow the paper definitions. Empty output is the empty string after
normalization, including whitespace-only text and markers such as <{silent}>.
Comparison is exact string match after normalization, not semantic equivalence.

R_ne is only defined when every reference is empty (non-speech subsets).
R_empty and R_nem require a non-empty reference.
PCP counts negated items whose non-empty, non-matching hypothesis hits T_ACP.
KW-ERR needs a keyword file (one term per line). The physician keyword list
used in the paper is not included.

  python scripts/score_drpf.py results.jsonl
  python scripts/score_drpf.py results.jsonl --keywords keywords.txt --neg-ids 2,6,9
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from settings import T_ACP  # noqa: E402
from text_norm import normalize_for_cer  # noqa: E402


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _norm(text: str) -> str:
    return normalize_for_cer(text or "")


def score_rates(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        raise SystemExit("No rows to score")
    refs = [_norm(r.get("ref", "")) for r in rows]
    hyps = [_norm(r.get("hyp", "")) for r in rows]
    speech = [i for i, ref in enumerate(refs) if ref]
    nonspeech = [i for i, ref in enumerate(refs) if not ref]

    def rate(hits: int, denom: int) -> float | None:
        if denom == 0:
            return None
        return round(hits / denom, 4)

    ne_hits = sum(1 for i in nonspeech if hyps[i])
    empty_hits = sum(1 for i in speech if not hyps[i])
    nem_hits = sum(1 for i in speech if hyps[i] and hyps[i] != refs[i])
    return {
        "n": n,
        "n_nonspeech": len(nonspeech),
        "n_speech": len(speech),
        "R_ne": rate(ne_hits, len(nonspeech)),
        "R_empty": rate(empty_hits, len(speech)),
        "R_nem": rate(nem_hits, len(speech)),
        "R_mismatch": rate(empty_hits + nem_hits, len(speech)),
    }


def score_pcp(rows: list[dict], neg_ids: set[str], triggers: tuple[str, ...] = T_ACP) -> dict:
    """PCP: negated item, non-empty hypothesis, hypothesis != reference, trigger hit."""
    selected = []
    for row in rows:
        item_id = str(row.get("id", row.get("sentence_id", "")))
        if row.get("negated") or item_id in neg_ids:
            selected.append(row)
    n = len(selected)
    hits = 0
    narrow = 0
    for row in selected:
        ref = _norm(row.get("ref", ""))
        hyp = _norm(row.get("hyp", ""))
        if not hyp or hyp == ref:
            continue
        matched = [t for t in triggers if _norm(t) in hyp]
        if matched:
            hits += 1
            if "服藥" in matched:
                narrow += 1
    return {"N_neg": n, "n_pcp": hits, "n_pcp_narrow": narrow, "R_pcp": round(hits / n, 4) if n else None}


def score_kwerr(rows: list[dict], keywords: list[str]) -> dict:
    """Keyword miss rate: each keyword counts at most once per utterance."""
    norms = [_norm(k) for k in keywords if _norm(k)]
    total = 0
    missed = 0
    for row in rows:
        ref = _norm(row.get("ref", ""))
        hyp = _norm(row.get("hyp", ""))
        expected = [k for k in norms if k in ref]
        total += len(expected)
        missed += sum(1 for k in expected if k not in hyp)
    return {
        "keyword_total": total,
        "keyword_miss": missed,
        "KW_ERR": round(missed / total, 4) if total else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score DRPF rates")
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--keywords", type=Path, help="One keyword per line. Not supplied with this release.")
    parser.add_argument("--neg-ids", default="", help="Comma-separated negated sentence ids for PCP")
    args = parser.parse_args()

    rows = _load_jsonl(args.jsonl)
    report = score_rates(rows)
    neg_ids = {part.strip() for part in args.neg_ids.split(",") if part.strip()}
    if neg_ids or any(r.get("negated") for r in rows):
        report["pcp"] = score_pcp(rows, neg_ids)
    if args.keywords:
        terms = [
            line.strip()
            for line in args.keywords.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        report["kwerr"] = score_kwerr(rows, terms)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
