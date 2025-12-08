# Faster Whisper 项目目录说明

## 📁 项目结构

```
faster-whisper/
├── 📁 faster_whisper/          # 核心库代码
│   ├── __init__.py            # 包初始化文件
│   ├── transcription.py      # 转录功能实现
│   ├── audio.py             # 音频处理工具
│   ├── utils.py             # 工具函数
│   └── models.py            # 模型相关
├── 📁 audio/                 # 音频文件存放目录
│   ├── ces.m4a              # 测试音频文件1
│   └── 3.m4a                # 测试音频文件2
├── 📁 models/                # Whisper模型文件
│   ├── whisper-base-ct2/    # Base模型（74MB）
│   └── whisper-large-v3-ct2/ # Large-v3模型（1550MB）
├── 📁 tests/                 # 测试文件
├── 📁 benchmark/             # 性能测试
├── 📁 .venv/                 # Python虚拟环境
├── 📄 run_basic.py           # 基础转录脚本
├── 📄 run_fast.py            # 快速转录脚本
├── 📄 run_simple.py          # 简单转录脚本
├── 📄 requirements.txt       # 项目依赖
├── 📄 setup.py              # 安装配置
├── 📄 README.md             # 项目说明文档
├── 📄 LICENSE               # 许可证
└── 📄 CONTRIBUTING.md       # 贡献指南
```

## 📋 文件详细说明

### 核心库 (faster_whisper/)
- **`__init__.py`**: 包的初始化文件，导出主要类和函数
- **`transcription.py`**: 实现语音转录的核心功能
- **`audio.py`**: 音频预处理和格式转换工具
- **`utils.py`**: 通用工具函数和辅助方法
- **`models.py`**: Whisper模型加载和管理

### 音频文件 (audio/)
- **`ces.m4a`**: 测试用的音频文件（中文语音）
- **`3.m4a`**: 另一个测试用的音频文件（中文语音）
- 支持格式：MP3, WAV, M4A, FLAC, OGG

### 模型文件 (models/)
- **`whisper-base-ct2/`**:
  - 大小：74MB
  - 特点：速度较快，准确度中等
  - 适合：实时转录或对速度要求高的场景
- **`whisper-large-v3-ct2/`**:
  - 大小：1550MB
  - 特点：准确度最高，速度较慢
  - 适合：对准确度要求高的离线转录

### 运行脚本
- **`run_basic.py`**: 基础转录功能演示
- **`run_fast.py`**: 优化的快速转录脚本
- **`run_simple.py`**: 最简单的转录示例

### 配置文件
- **`requirements.txt`**: Python依赖包列表
  - faster-whisper
  - torch
  - torchaudio
  - 其他必要依赖
- **`setup.py`**: 包安装和分发配置
- **`LICENSE`**: MIT许可证
- **`CONTRIBUTING.md`**: 项目贡献指南

## 🚀 快速开始

### 1. 环境准备
```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行转录
```bash
# 基础转录
python run_basic.py

# 快速转录
python run_fast.py

# 简单转录
python run_simple.py
```

## 📖 使用说明

### 支持的音频格式
- ✅ MP3
- ✅ WAV
- ✅ M4A
- ✅ FLAC
- ✅ OGG

### 支持的语言
- 🌐 自动检测（默认）
- 🇨🇳 中文 (zh)
- 🇺🇸 英文 (en)
- 🇯🇵 日文 (ja)
- 🇰🇷 韩文 (ko)
- 🇪🇸 西班牙文 (es)
- 🇫🇷 法文 (fr)
- 🇩🇪 德文 (de)
- 以及更多...

### 配置选项
- **模型选择**: base, large-v3
- **计算设备**: CPU, GPU (CUDA)
- **VAD过滤**: 语音活动检测
- **语言设置**: 自动检测或指定语言
- **输出格式**: 纯文本, SRT字幕, JSON

## 🔧 开发说明

### 添加新功能
1. 在 `faster_whisper/` 目录下添加新模块
2. 更新 `__init__.py` 导出新功能
3. 在 `tests/` 目录添加对应测试
4. 更新此文档说明新功能

### 性能优化
- 使用合适的模型大小（base vs large-v3）
- 启用GPU加速（如果有CUDA）
- 调整VAD参数
- 批量处理多个文件

### 故障排除
1. 模型文件不存在 → 检查 `models/` 目录
2. 音频格式不支持 → 转换为支持的格式
3. 内存不足 → 使用base模型或CPU模式
4. 速度太慢 → 检查是否使用GPU或base模型

## 📊 性能参考

| 模型 | 大小 | 速度 | 准确度 | 推荐用途 |
|------|------|------|--------|----------|
| base | 74MB | 快 | 中等 | 实时转录 |
| large-v3 | 1550MB | 慢 | 最高 | 离线转录 |

## 📝 更新日志

- **v1.2.1**: 最新版本，支持最新的模型和功能
- 包含CTranslate2优化
- 支持实时转录
- 改进的VAD过滤