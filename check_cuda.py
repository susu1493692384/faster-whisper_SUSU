#!/usr/bin/env python3
"""
检查CUDA和PyTorch支持
"""
import sys
import os

def check_cuda_support():
    """检查CUDA支持"""
    try:
        # 首先检查是否有NVIDIA驱动
        import subprocess
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("NVIDIA驱动已安装")
                # 检查CUDA版本
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'CUDA Version:' in line:
                        print(f"CUDA版本: {line.strip()}")
                        break
            else:
                print("NVIDIA驱动未找到")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("无法运行nvidia-smi，NVIDIA驱动可能未安装")
            return False

        # 尝试导入torch检查CUDA
        try:
            import torch
            if torch.cuda.is_available():
                print(f"PyTorch CUDA支持: 可用")
                print(f"CUDA设备数量: {torch.cuda.device_count()}")
                if torch.cuda.device_count() > 0:
                    print(f"当前GPU: {torch.cuda.get_device_name(0)}")
                return True
            else:
                print("PyTorch CUDA支持: 不可用")
                return False
        except ImportError:
            print("PyTorch未安装，无法检查CUDA支持")
            return False

    except Exception as e:
        print(f"检查CUDA时出错: {e}")
        return False

def check_cpu_fallback():
    """检查CPU回退选项"""
    print("\nCPU模式信息:")
    try:
        import platform
        print(f"系统: {platform.system()} {platform.release()}")
        print(f"处理器: {platform.processor()}")

        # 检查CPU核心数
        import multiprocessing
        print(f"CPU核心数: {multiprocessing.cpu_count()}")

        return True
    except Exception as e:
        print(f"检查CPU信息时出错: {e}")
        return False

if __name__ == "__main__":
    print("=== GPU/CPU 支持检查 ===")

    has_cuda = check_cuda_support()
    check_cpu_fallback()

    if has_cuda:
        print("\n结果: 建议使用GPU版本")
        print("CUDA_AVAILABLE")
    else:
        print("\n结果: 将使用CPU版本")
        print("CPU_ONLY")