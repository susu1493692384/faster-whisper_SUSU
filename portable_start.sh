#!/bin/bash

echo "========================================"
echo "   Faster Whisper GUI 便携版启动器"
echo "========================================"
echo

# 检查Python环境
if [ -f "python/bin/python3" ]; then
    echo "使用内置Python环境..."
    PYTHON_PATH="python/bin/python3"
elif command -v python3 &> /dev/null; then
    echo "使用系统Python3..."
    PYTHON_PATH="python3"
elif command -v python &> /dev/null; then
    echo "使用系统Python..."
    PYTHON_PATH="python"
else
    echo "错误：未找到Python环境，请先安装Python"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo
    echo "正在初始化虚拟环境..."
    $PYTHON_PATH -m venv .venv

    if [ $? -eq 0 ]; then
        echo "正在安装依赖..."
        .venv/bin/pip install -r requirements.txt

        if [ $? -ne 0 ]; then
            echo "依赖安装失败，请检查网络连接"
            exit 1
        fi
    else
        echo "虚拟环境创建失败"
        exit 1
    fi
fi

# 激活虚拟环境并启动GUI
echo
echo "正在启动Faster Whisper GUI..."
source .venv/bin/activate && python gui_transcriber.py

if [ $? -ne 0 ]; then
    echo
    echo "启动失败，请检查错误信息"
    read -p "按回车键继续..."
fi