"""Published deployment settings for the DRPF case study.

Cloud API language-parameter values are not included.
"""

SAMPLE_RATE = 16000

# Public Whisper contrast arm.
WHISPER_MODEL_ID = "openai/whisper-large-v3-turbo"
WHISPER_LANGUAGE = "zh"

# Edge pipeline.
NEMOTRON_MODEL_ID = "nvidia/nemotron-3.5-asr-streaming-0.6b"
NEMOTRON_LANGUAGE = "zh-CN"

# Silero VAD gate used in the VAD contrast.
VAD_THRESHOLD = 0.5

# Traditional-Chinese post-processing used by every pipeline in the paper.
OPENCC_CONFIG = "s2twp"

# PCP trigger set published for the ACP case. Finance and law trigger
# lists are not released.
T_ACP = ("服藥", "插管", "急救")
