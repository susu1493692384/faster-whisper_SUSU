import os
import time
from faster_whisper import WhisperModel

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
AUDIO_FILE = os.path.join(AUDIO_DIR, "ces.m4a")
model_path = os.path.join(MODEL_DIR, "whisper-large-v3-ct2")

print("FAST转录模式启动...")
print(f"音频文件: {AUDIO_FILE}")

# 最小化模型设置
model = WhisperModel(
    model_path,
    device="cpu",  # 使用CPU避免GPU瓶颈
    compute_type="int8",  # 使用int8精度提高速度
)

# 最激进的转录设置
segments, info = model.transcribe(
    AUDIO_FILE,
    language="zh",
    beam_size=1,           # 最小beam size
    best_of=1,             # 只尝试一次
    temperature=0.0,       # 确定性输出
    compression_ratio_threshold=2.4,  # 压缩阈值
    log_prob_threshold=-1.0,
    no_speech_threshold=0.6,
    word_timestamps=False,  # 不需要词级别时间戳
    condition_on_previous_text=False,  # 不依赖前文
    vad_filter=True,       # 启用VAD过滤
    vad_parameters=dict(min_silence_duration_ms=500),  # 更激进的静音过滤
    max_initial_timestamp=0.0,
)

print(f"检测语言: {info.language} (置信度: {info.language_probability})")
print("开始快速转录...")

segment_count = 0
start_time = time.time()

for segment in segments:
    segment_count += 1
    current_time = time.time()
    elapsed = current_time - start_time

    # 只打印文本，减少I/O开销
    print(f"[{segment.start:.1f}s] {segment.text.strip()}")

    # 显示速度统计
    if segment_count % 5 == 0:
        real_time_factor = elapsed / segment.end if segment.end > 0 else 0
        print(f"速度: {real_time_factor:.1f}x realtime, 片段数: {segment_count}")

total_time = time.time() - start_time
print(f"\n完成! 总用时: {total_time:.1f}s, 处理了 {segment_count} 个片段")