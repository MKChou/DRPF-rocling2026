# DRPF: Deployment Risk Probe Framework

Probe sets and scoring code for the ROCLING 2026 paper **Deployment Risk Probe Framework (DRPF): Complementing CER with Actionable Failure Modes**.

DRPF splits ASR errors into three types. Each type calls for a different follow-up action:

| Error type | Rate | Follow-up |
| --- | --- | --- |
| (i) Text on non-speech input | R_ne | Filter the input or tune VAD |
| (ii) Empty output on speech | R_empty | Ask the user to repeat; never default to consent |
| (iii) Incorrect content on speech | R_nem | Manual verification |

The polarity-conflict probe (PCP) is a narrow subset of (iii). It flags negated short answers whose transcript contains a high-risk action word, such as 不要了 becoming 服藥了 ("take medication").

## Contents

```
data/
  c1_silence/          C1: 100 digital-silence clips (3/5/8/10 s × 25), 16 kHz mono
  c2b/README.md        C2B: DEMAND scenes, license and archive checksums
  manifests/           C1 and C2B manifests (paths, offsets, durations)
  scripts/             C3 short-answer and C4 hesitation scripts (Mandarin)
drpf/
  text_norm.py         Normalization: NFKC, OpenCC s2twp, strip punctuation, whitespace and <{silent}>
  score_drpf.py        R_ne, R_empty, R_nem, CER, PCP and KW-ERR
  vad_gate.py          Silero VAD gate (threshold 0.5)
  settings.py          Model IDs, language settings, VAD threshold, OpenCC config, ACP triggers
  build_c2b.py         Rebuilds the C2B clips from DEMAND
results/
  paper_counts.md      Aggregate counts reported in the paper
```

## Probe sets

| Subset | Role | Released here |
| --- | --- | --- |
| C1 | (i) digital silence | Audio and manifest |
| C2B | (i) environmental noise, five DEMAND scenes | Manifest; audio rebuilt by `drpf/build_c2b.py` |
| C3 | (ii), (iii) and PCP on short answers | Script: 50 items (24 confirm, 19 negate, 7 other) |
| C4 | (ii), (iii) on hesitations and fillers | Script: 50 items |

The PCP set is the 19 C3 items marked `negate` in `data/scripts/c3_short.tsv`.

To record C3 and C4, use 16 kHz mono WAV and one file per item. Trim long leading and trailing silence from C3 clips. Keep C4 fillers as spoken, without turning them into full sentences.

## Setup

Python 3.10 or later.

```bash
pip install -r requirements.txt
```

`vad_gate.py` downloads Silero VAD through `torch.hub` on first use.

## Scoring

Write ASR outputs as JSONL, one segment per line. Leave `ref` empty for non-speech segments. `id` is only needed for PCP.

```json
{"id": "009", "ref": "不要了", "hyp": "服藥了"}
{"id": "silence_01_3s", "ref": "", "hyp": ""}
```

```bash
python drpf/score_drpf.py outputs.jsonl
python drpf/score_drpf.py outputs.jsonl --neg-from data/scripts/c3_short.tsv
python drpf/score_drpf.py outputs.jsonl --keywords keywords.txt
```

After normalization, empty strings, whitespace-only output and markers such as `<{silent}>` all count as empty output. A hypothesis matches only if it equals the reference exactly after normalization.

R_ne uses segments with an empty reference. R_empty, R_nem and CER use segments with a non-empty reference. KW-ERR takes a keyword list with one term per line.

## Rebuilding C2B

```bash
python drpf/build_c2b.py
```

The script downloads the five 16 kHz DEMAND archives from Zenodo, checks their SHA-256, takes channel 01 and writes the 100 clips to `data/c2b/audio/`.

## Not included

- C2A hospital background noise
- Individual speaker recordings
- Internal language-setting values of the cloud API
- Held-out, finance and legal scripts
- C5 clinic sentences and the physician keyword list

Scores depend on recordings, API versions and environment. Rerunning the probes on new recordings should reproduce the structure of the results, not the exact values in `results/paper_counts.md`.

## License

Code and C1 audio are released under the MIT License. DEMAND audio used for C2B remains under CC BY-SA 3.0.

## Citation

```bibtex
@inproceedings{chou2026drpf,
  title     = {Deployment Risk Probe Framework ({DRPF}): Complementing {CER} with Actionable Failure Modes},
  author    = {Chou, Ming-Kun and Lo, Yu-Tai and Lu, Wen-Hsiang},
  booktitle = {Proceedings of the 38th Conference on Computational Linguistics and Speech Processing (ROCLING 2026)},
  year      = {2026}
}
```
