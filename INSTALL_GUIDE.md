# 📦 安装指南

## 🎯 快速开始

### 1. 环境检查
确保你的系统已安装：
- Python 3.8-3.11 (推荐 3.11)
- CUDA 11.8+ (如需GPU支持)
- Git

### 2. 克隆项目
```bash
git clone <项目仓库地址>
cd faster-whisper
```

### 3. 创建虚拟环境
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 4. 安装依赖
```bash
# 方式1: 安装所有依赖（推荐）
pip install -r requirements.txt

# 方式2: 仅安装核心依赖（更快）
pip install faster-whisper torch torchaudio av PyYAML tqdm click ctranslate2 onnxruntime

# 方式3: 如果需要GPU支持
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

### 5. 下载模型
将模型文件放入 `models/` 目录：
- `models/whisper-base-ct2/`
- `models/whisper-large-v3-ct2/`

### 6. 启动应用
```bash
# GUI转录工具
python gui_transcriber.py

# 或使用启动脚本
python start_gui.py
```

## 🔧 依赖说明

### 核心依赖（必需）
- `faster-whisper`: Whisper转录引擎
- `ctranslate2`: 模型推理优化
- `torch/torchaudio`: 深度学习框架
- `av`: 音频处理库
- `PyYAML`: 配置文件解析

### GUI界面（必需）
- `tkinter`: Python内置GUI库
  - Windows: 已包含在Python安装中
  - Linux: `sudo apt-get install python3-tk`
  - Mac: 已包含在Python安装中

### 音频格式支持
支持的格式：MP3, WAV, M4A, FLAC, OGG

## 🖥️ Windows特别说明

### GPU支持
如果有NVIDIA GPU和CUDA：
```bash
# 1. 检查CUDA版本
nvidia-smi

# 2. 安装CUDA版本的PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. 验证CUDA支持
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### 本地PyTorch安装
如果有预编译的wheel文件：
```bash
pip install "path\to\torch-2.6.0+cu124-cp313-cp313-win_amd64.whl"
```

## 🌐 可选功能

### Web服务器
如需Web接口，取消注释requirements.txt中的Web依赖：
```python
# fastapi>=0.104.0
# uvicorn[standard]>=0.24.0
# ...
```

### SenseVoice模型
如需使用SenseVoice，需要ESPnet（Windows安装困难）：
```python
# espnet
# espnet-model-zoo
```

## ⚡ 性能优化

### GPU加速
- 使用Base模型获得最佳速度
- Large-v3模型获得最佳准确度
- GPU比CPU快5-10倍

### VAD过滤
- 启用VAD语音活动检测
- 提高转录准确度
- 减少无语音段错误

### 内存优化
- CT2格式模型比原始模型更小
- 支持批量处理

## 🚀 故障排除

### 常见问题

1. **CUDA不可用**
   ```bash
   # 检查CUDA版本
   nvidia-smi

   # 检查PyTorch版本
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **模块未找到**
   ```bash
   # 重新安装
   pip install --upgrade <module_name>
   ```

3. **模型文件不存在**
   - 下载CT2格式模型到 `models/` 目录
   - 推荐使用huggingface模型转换

4. **音频格式不支持**
   - 使用ffmpeg转换格式
   - `ffmpeg -i input.wav -ar 16000 output.wav`

### 环境变量
设置CUDA环境变量（如需要）：
```bash
# Windows
set CUDA_VISIBLE_DEVICES=0

# Linux/Mac
export CUDA_VISIBLE_DEVICES=0
```

## 📊 版本兼容性

| Python版本 | Windows | Linux | Mac | 说明 |
|-------------|---------|-------|-----|------|
| 3.8 | ✅ | ✅ | ✅ | 稳定 |
| 3.9 | ✅ | ✅ | ✅ | 稳定 |
| 3.10 | ✅ | ✅ | ✅ | 推荐 |
| 3.11 | ✅ | ✅ | ✅ | 最新 |
| 3.12+ | ⚠️ | ⚠️ | ⚠️ | 可能有问题 |

## 💡 使用技巧

1. **首次使用**
   - 选择Base模型测试
   - 使用短音频文件验证

2. **生产环境**
   - 使用Large-v3模型
   - 启用GPU加速
   - 批量处理文件

3. **内存限制**
   - 使用Base模型
   - 分段处理长音频
   - 定期清理临时文件

4. **多语言支持**
   - 设置language参数
   - 使用language="auto"自动检测

## 🎉 完成！

安装完成后，你就可以使用高性能的语音转录功能了！

- 🎤 **GUI工具**: `python gui_transcriber.py`
- 📝 **实时转录**: 支持实时显示进度
- 💾 **结果导出**: 多格式导出功能
- 🚀 **GPU加速**: 5-10倍速度提升