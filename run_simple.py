import os
import time
from faster_whisper import WhisperModel

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
AUDIO_FILE = os.path.join(AUDIO_DIR, "ces.m4a")

print("Simple Whisper transcription")
print(f"Audio file: {AUDIO_FILE}")

# 使用本地large-v3模型
model_path = os.path.join(MODEL_DIR, "whisper-large-v3-ct2")
model = WhisperModel(
    model_path,
    device="cpu",
    compute_type="int8"  # 使用int8提高速度
)

print("Starting transcription...")
start_time = time.time()

# 简化的转录参数
segments, info = model.transcribe(
    AUDIO_FILE,
    language="zh",
    beam_size=1,           # 最小beam
    vad_filter=True        # 启用VAD过滤静音
)

print(f"Detected language: {info.language}")

segment_count = 0
for segment in segments:
    segment_count += 1
    print(f"[{segment.start:.1f}s] {segment.text.strip()}")

total_time = time.time() - start_time
print(f"\nCompleted in {total_time:.1f}s, {segment_count} segments")