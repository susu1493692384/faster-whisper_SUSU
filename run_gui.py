#!/usr/bin/env python3
"""
超级简化启动脚本 - 直接运行GUI
"""

try:
    print("启动 Faster Whisper GUI...")
    from gui_transcriber import WhisperGUI
    app = WhisperGUI()
    app.run()
except ImportError:
    print("错误：无法导入 gui_transcriber.py")
    print("请确保该文件存在并且可以访问")
    input("按回车键退出...")
except Exception as e:
    print(f"错误：{e}")
    input("按回车键退出...")