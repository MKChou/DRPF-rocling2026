# Aggregate counts reported in the paper

These are the aggregate counts from the paper's tables. They cannot be recomputed from this repository because the speech recordings are not released.

Pipelines:

- **Cloud**: remote Whisper large-v3-turbo with built-in VAD and OpenCC `s2twp`. `lang-med` is the main language setting and `lang-base` the contrast.
- **Edge**: Nemotron 3.5 ASR 0.6B, `zh-CN`, OpenCC `s2twp`, no added VAD unless marked +VAD.
- **Public Whisper**: `openai/whisper-large-v3-turbo`, with or without Silero VAD (threshold 0.5).

Error types:

- **(i)** text on non-speech input (R_ne)
- **(ii)** empty output on speech (R_empty)
- **(iii)** incorrect content on speech (R_nem)

Mismatch is (ii) + (iii).

## Short-answer probes

(i) is reported for each non-speech subset (C1, C2A, C2B) with N = 100. The other columns cover C3 + C4 with N = 400 (four speakers).

| Setting | (i), each | Mismatch | (ii) | (iii) |
| --- | --- | --- | --- | --- |
| Cloud + lang-med | 0/100 | 259/400 | 16/400 | 243/400 |
| Cloud + lang-base | 0/100 | 128/400 | 16/400 | 112/400 |
| Edge | 0/100 | 132/400 | 72/400 | 60/400 |
| Public Whisper | 100/100 | 133/400 | 0/400 | 133/400 |
| Public Whisper + VAD | 0/100 | 145/400 | 16/400 | 129/400 |
| Edge + VAD | 0/100 | 145/400 | 80/400 | 65/400 |

## Polarity-conflict probe (ACP)

PCP counts negated short answers whose output contains one of the ACP triggers 服藥, 插管 or 急救. PCP-narrow counts only 服藥. The denominator is 19 negated scripts × 4 speakers = 76.

| Setting | PCP | PCP-narrow |
| --- | --- | --- |
| Cloud + lang-med | 20/76 | 19/76 |
| Cloud + lang-base | 0/76 | 0/76 |
| Edge | 0/76 | 0/76 |

For Cloud + lang-med, the per-speaker counts are 8/19, 1/19, 6/19 and 5/19. On the held-out negated set (N = 120), PCP is 24/120.

## C5 clinic sentences: CER and KW-ERR (%, N = 200)

| Setting | CER | KW-ERR |
| --- | --- | --- |
| Cloud + lang-med | 11.2 | 48.2 |
| Cloud + lang-base | 3.9 | 14.3 |
| Edge | 7.6 | 42.9 |
| Edge + VAD | 7.8 | 42.0 |
| Public Whisper | 12.3 | 27.7 |
| Public Whisper + VAD | 4.4 | 26.8 |

## Context benchmarks (%)

Mandarin and Taiwanese use 500 sentences each. Taiwanese lexical hit rate is keyword recall against word-level annotations. The Taiwanese setting is only available in the cloud pipeline.

| Setting | Mandarin CER | Taiwanese CER | Taiwanese lexical hit |
| --- | --- | --- | --- |
| Cloud + lang-med | 6.5 | 9.0 | 86.1 |
| Cloud + lang-base | 2.6 | 88.4 | 11.2 |
| Edge | 5.6 | — | — |

## Cross-domain mini-probes

Finance and Law PCP use domain-specific trigger sets. The denominator is 18 negated scripts × 4 speakers = 72. Prior-leak counts non-ACP outputs that contain an ACP trigger, over all 120 short answers in the domain.

| Setting | Finance PCP | Finance Prior-leak | Law PCP | Law Prior-leak |
| --- | --- | --- | --- | --- |
| Cloud + lang-med | 10/72 | 14/120 | 6/72 | 12/120 |
| Cloud + lang-base | 0/72 | 0/120 | 0/72 | 0/120 |
| Edge | 1/72 | 0/120 | 0/72 | 0/120 |
