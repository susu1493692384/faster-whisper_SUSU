import os
import time
from faster_whisper import WhisperModel

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
AUDIO_FILE = os.path.join(AUDIO_DIR, "ces2.m4a")  # 替换为你的音频文件名

print(f"音频文件: {AUDIO_FILE}")

# 使用转换后的base模型
model_path = os.path.join(MODEL_DIR, "whisper-large-v3-ct2")
model = WhisperModel(model_path, device="cpu", compute_type="int8")

# 基础转录设置
segments, info = model.transcribe(
    AUDIO_FILE,
    language="zh",
    beam_size=1,
    best_of=1,
    temperature=0.0,
    word_timestamps=False,
    condition_on_previous_text=False,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
)

print(f"检测语言: {info.language} (置信度: {info.language_probability})")
print("开始转录...")

segment_count = 0
start_time = time.time()

for segment in segments:
    segment_count += 1
    print(f"[{segment.start:.1f}s] {segment.text.strip()}")

    # 显示进度
    if segment_count % 5 == 0:
        elapsed = time.time() - start_time
        real_time_factor = elapsed / segment.end if segment.end > 0 else 0
        print(f"进度: {segment_count} 片段, 速度: {real_time_factor:.1f}x realtime")

total_time = time.time() - start_time
print(f"\n完成! 总用时: {total_time:.1f}s, 处理了 {segment_count} 个片段")

