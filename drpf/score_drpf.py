"""Score DRPF rates, CER, PCP and KW-ERR from ASR outputs.

Input is JSONL with one record per segment:

    {"id": "009", "ref": "不要了", "hyp": "服藥了"}

``ref`` is empty for non-speech segments (C1, C2B). ``id`` is only needed for
PCP. After normalization, empty strings, whitespace and markers such as
``<{silent}>`` all count as empty output. Matching is exact string equality
after normalization.

    python drpf/score_drpf.py outputs.jsonl
    python drpf/score_drpf.py outputs.jsonl --neg-from data/scripts/c3_short.tsv
    python drpf/score_drpf.py outputs.jsonl --keywords my_keywords.txt
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from settings import PCP_NARROW_TRIGGER, T_ACP  # noqa: E402
from text_norm import normalize_for_cer  # noqa: E402


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def norm_id(value: object) -> str:
    text = str(value).strip()
    return text.lstrip("0") or ("0" if text else "")


def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def ratio(hits: int, denom: int) -> float | None:
    return round(hits / denom, 4) if denom else None


def score_rates(refs: list[str], hyps: list[str]) -> dict:
    """R_ne on segments with an empty reference; R_empty and R_nem on the rest."""
    speech = [i for i, ref in enumerate(refs) if ref]
    nonspeech = [i for i, ref in enumerate(refs) if not ref]
    ne = sum(1 for i in nonspeech if hyps[i])
    empty = sum(1 for i in speech if not hyps[i])
    nem = sum(1 for i in speech if hyps[i] and hyps[i] != refs[i])
    return {
        "n_nonspeech": len(nonspeech),
        "n_speech": len(speech),
        "R_ne": ratio(ne, len(nonspeech)),
        "R_empty": ratio(empty, len(speech)),
        "R_nem": ratio(nem, len(speech)),
        "R_mismatch": ratio(empty + nem, len(speech)),
        "counts": {"ne": ne, "empty": empty, "nem": nem},
    }


def score_cer(refs: list[str], hyps: list[str]) -> float | None:
    """Corpus CER over speech segments: total edit distance / total reference characters."""
    pairs = [(r, h) for r, h in zip(refs, hyps) if r]
    total = sum(len(r) for r, _ in pairs)
    if not total:
        return None
    return round(sum(edit_distance(r, h) for r, h in pairs) / total, 4)


def score_pcp(refs: list[str], hyps: list[str], negated: list[bool]) -> dict:
    """Negated segment, non-empty hypothesis != reference, hypothesis contains a trigger."""
    triggers = [normalize_for_cer(t) for t in T_ACP]
    narrow_trigger = normalize_for_cer(PCP_NARROW_TRIGGER)
    idx = [i for i, flag in enumerate(negated) if flag]
    hits = narrow = 0
    for i in idx:
        hyp = hyps[i]
        if not hyp or hyp == refs[i]:
            continue
        if any(t in hyp for t in triggers):
            hits += 1
            if narrow_trigger in hyp:
                narrow += 1
    return {
        "N_neg": len(idx),
        "n_pcp": hits,
        "n_pcp_narrow": narrow,
        "R_pcp": ratio(hits, len(idx)),
    }


def score_kwerr(refs: list[str], hyps: list[str], keywords: list[str]) -> dict:
    """Keywords present in the reference but missing from the hypothesis; each counted once per segment."""
    terms = list(dict.fromkeys(k for k in (normalize_for_cer(k) for k in keywords) if k))
    total = missed = 0
    for ref, hyp in zip(refs, hyps):
        expected = [k for k in terms if k in ref]
        total += len(expected)
        missed += sum(1 for k in expected if k not in hyp)
    return {"keyword_total": total, "keyword_missed": missed, "KW_ERR": ratio(missed, total)}


def negated_ids_from_tsv(path: Path) -> set[str]:
    with path.open(encoding="utf-8", newline="") as f:
        return {norm_id(r["id"]) for r in csv.DictReader(f, delimiter="\t") if r["category"] == "negate"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Score DRPF rates")
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--neg-from", type=Path, help="Script TSV; rows with category 'negate' form the PCP set")
    parser.add_argument("--neg-ids", default="", help="Comma-separated ids to treat as negated")
    parser.add_argument("--keywords", type=Path, help="Keyword list for KW-ERR, one term per line")
    args = parser.parse_args()

    rows = load_jsonl(args.jsonl)
    if not rows:
        raise SystemExit(f"No records in {args.jsonl}")
    refs = [normalize_for_cer(r.get("ref", "")) for r in rows]
    hyps = [normalize_for_cer(r.get("hyp", "")) for r in rows]

    report = {"n": len(rows), **score_rates(refs, hyps), "CER": score_cer(refs, hyps)}

    neg_ids = {norm_id(x) for x in args.neg_ids.split(",") if x.strip()}
    if args.neg_from:
        neg_ids |= negated_ids_from_tsv(args.neg_from)
    if neg_ids:
        negated = [norm_id(r.get("id", "")) in neg_ids for r in rows]
        report["PCP"] = score_pcp(refs, hyps, negated)

    if args.keywords:
        lines = args.keywords.read_text(encoding="utf-8").splitlines()
        terms = [x.strip() for x in lines if x.strip() and not x.lstrip().startswith("#")]
        report["KW_ERR"] = score_kwerr(refs, hyps, terms)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
