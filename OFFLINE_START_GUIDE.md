# Offline Start Script 使用指南

## 功能概述

修改后的 `offline_start.cmd` 具有以下智能功能：

### 1. 环境检查
- 自动检测Python环境（内置Python、系统Python）
- 检查虚拟环境是否已存在
- 智能CUDA支持检测

### 2. 智能安装
- **GPU优先**: 如果检测到CUDA支持，优先安装GPU版本的PyTorch
- **CPU回退**: 如果GPU安装失败或无CUDA，自动使用CPU版本
- **完全离线**: 所有安装都使用本地packages文件夹，无需网络连接

### 3. 文件结构要求
```
dist_offline_complete/
├── offline_start.cmd          # 修改后的启动脚本
├── check_cuda.py              # CUDA检查脚本
├── requirements.txt           # CPU版本依赖
├── requirements_gpu.txt       # GPU版本依赖
├── packages/                  # CPU版本离线包
├── packages_gpu/              # GPU版本离线包（可选）
├── models/                    # 模型文件目录
│   └── whisper-base-ct2/
│       └── model.bin
└── gui_transcriber.py         # GUI主程序
```

## 使用方法

### 简单启动
```cmd
cd dist_offline_complete
offline_start.cmd
```

### 工作流程

1. **环境检查阶段**
   - 检查Python环境是否可用
   - 检查虚拟环境是否存在

2. **环境创建阶段**（仅在首次运行时）
   - 创建Python虚拟环境
   - 运行CUDA检测脚本
   - 根据检测结果选择GPU或CPU版本

3. **依赖安装阶段**
   - GPU模式: 使用packages_gpu和requirements_gpu.txt
   - CPU模式: 使用packages和requirements.txt

4. **应用启动阶段**
   - 检查模型文件
   - 启动GUI界面

## CUDA检测逻辑

### 检测步骤
1. 检查NVIDIA驱动（nvidia-smi）
2. 检查PyTorch CUDA支持
3. 输出GPU/CPU模式信息

### 输出示例
```
=== GPU/CPU 支持检查 ===
NVIDIA驱动已安装
CUDA版本: 12.4
PyTorch CUDA支持: 可用
CUDA设备数量: 1
当前GPU: NVIDIA GeForce RTX 4090

系统: Windows 10
处理器: Intel64 Family 6 Model 183 Stepping 1, GenuineIntel
CPU核心数: 16

结果: 建议使用GPU版本
CUDA_AVAILABLE
```

## 错误处理

### 常见错误及解决方案

1. **Python环境未找到**
   - 安装Python 3.8+
   - 或将python文件夹放在当前目录

2. **虚拟环境创建失败**
   - 确保Python版本兼容
   - 检查磁盘空间
   - 确保写入权限

3. **GPU包安装失败**
   - 自动回退到CPU版本
   - 检查packages_gpu文件夹是否存在

4. **模型文件未找到**
   - 确保models文件夹存在
   - 确保whisper-base-ct2/model.bin存在

## 性能优化

### GPU版本优势
- **转录速度**: 提升3-10倍
- **大模型支持**: 更好的内存管理
- **并行处理**: 充分利用GPU并行性

### CPU版本特点
- **兼容性好**: 适用于所有机器
- **安装简单**: 无需额外驱动
- **内存友好**: 占用内存相对较少

## 技术细节

### 脚本特性
- **延迟扩展**: 支持变量在if块内正确更新
- **错误捕获**: 每个步骤都有错误检查
- **优雅降级**: GPU失败自动使用CPU

### 检查脚本功能
- **NVIDIA驱动检测**: 调用nvidia-smi
- **PyTorch兼容性**: 检查torch.cuda.is_available()
- **系统信息**: 显示CPU和系统信息

## 故障排除

### 启动失败
1. 检查Python是否正确安装
2. 查看错误信息并对应解决
3. 确保所有文件完整性

### 性能问题
1. 确认是否使用了正确的版本（GPU/CPU）
2. 检查GPU驱动是否最新
3. 优化模型选择和参数设置

### 离线安装问题
1. 确保packages文件夹存在且完整
2. 检查requirements.txt文件
3. 验证Python版本兼容性

通过这个修改后的启动脚本，用户可以获得最优的性能体验，同时保持完全的离线兼容性。