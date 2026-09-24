"""Pipeline settings reported in the paper."""

SAMPLE_RATE = 16000

# Public Whisper contrast arm.
WHISPER_MODEL_ID = "openai/whisper-large-v3-turbo"
WHISPER_LANGUAGE = "zh"

# Edge pipeline.
NEMOTRON_MODEL_ID = "nvidia/nemotron-3.5-asr-streaming-0.6b"
NEMOTRON_LANGUAGE = "zh-CN"

# Silero VAD threshold for the +VAD contrasts.
VAD_THRESHOLD = 0.5

# Traditional-Chinese conversion applied to every pipeline output.
OPENCC_CONFIG = "s2twp"

# ACP trigger set for the polarity-conflict probe (PCP).
T_ACP = ("服藥", "插管", "急救")
PCP_NARROW_TRIGGER = "服藥"
