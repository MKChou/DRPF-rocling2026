"""Silero VAD gate: no speech yields empty output; speech segments are concatenated before ASR."""

from __future__ import annotations

import numpy as np
import torch

from settings import SAMPLE_RATE, VAD_THRESHOLD

_model = None
_get_speech_timestamps = None


def load_vad() -> None:
    global _model, _get_speech_timestamps
    if _model is not None:
        return
    model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        trust_repo=True,
    )
    _model = model
    _get_speech_timestamps = utils[0]


def speech_segments(
    audio: np.ndarray,
    *,
    threshold: float = VAD_THRESHOLD,
    sampling_rate: int = SAMPLE_RATE,
) -> list[dict]:
    """Return Silero timestamps in samples; an empty list means no speech."""
    load_vad()
    wav = torch.from_numpy(np.asarray(audio, dtype=np.float32))
    if wav.ndim > 1:
        wav = wav.mean(dim=-1)
    return _get_speech_timestamps(
        wav,
        _model,
        sampling_rate=sampling_rate,
        threshold=threshold,
    )


def apply_vad_gate(
    audio: np.ndarray,
    *,
    threshold: float = VAD_THRESHOLD,
    sampling_rate: int = SAMPLE_RATE,
) -> tuple[np.ndarray | None, bool]:
    """Return ``(gated_audio, has_speech)``.

    ``gated_audio`` is ``None`` when no speech is detected; the caller should
    then emit an empty transcript instead of running ASR.
    """
    stamps = speech_segments(audio, threshold=threshold, sampling_rate=sampling_rate)
    if not stamps:
        return None, False
    chunks = [audio[int(s["start"]) : int(s["end"])] for s in stamps]
    return np.concatenate(chunks).astype(np.float32), True
