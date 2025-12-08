#!/usr/bin/env python3
"""
Faster Whisper GUI 转录工具
支持实时显示的图形界面转录应用
"""

import os
import sys
import threading
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter.scrolledtext as ScrolledText

import torch
from faster_whisper import WhisperModel

# 在打包时添加资源文件路径
def get_resource_path(relative_path):
    """获取打包后的资源文件路径"""
    try:
        # PyInstaller创建临时文件夹，将资源文件存储在其中
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境下的路径
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 确保VAD模型文件可用
def ensure_vad_model():
    """确保VAD模型文件存在"""
    try:
        from faster_whisper.vad import get_vad_model
        from faster_whisper.utils import get_assets_path

        # 获取VAD模型文件路径
        model_path = os.path.join(get_assets_path(), "silero_vad_v6.onnx")
        if os.path.exists(model_path):
            return model_path

        # 如果模型不存在，尝试从打包的资源中复制
        resource_path = get_resource_path('faster_whisper/assets/silero_vad_v6.onnx')
        if os.path.exists(resource_path):
            # 创建目录并复制文件
            cache_dir = os.path.join(os.path.expanduser('~'), '.cache', 'faster_whisper')
            os.makedirs(cache_dir, exist_ok=True)
            target_path = os.path.join(cache_dir, 'silero_vad_v6.onnx')

            if not os.path.exists(target_path):
                import shutil
                shutil.copy2(resource_path, target_path)

            return target_path

    except Exception as e:
        print(f"VAD模型检查警告: {e}")
        return None


class WhisperGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Faster Whisper 实时转录")
        self.root.geometry("1000x800")  # 增大窗口尺寸
        self.root.minsize(900, 700)    # 设置最小尺寸

        # 设置样式
        self.root.configure(bg='#f0f0f0')
        self.setup_styles()

        # 变量
        self.model = None
        self.current_file = None
        self.transcribing = False
        self.transcription_thread = None

        # 设置变量
        self.file_var = tk.StringVar()
        self.model_var = tk.StringVar(value="whisper-large-v3-ct2")
        self.device_var = tk.StringVar(value="cpu")
        self.vad_var = tk.BooleanVar(value=True)
        self.word_timestamps_var = tk.BooleanVar(value=True)
        self.language_var = tk.StringVar(value="zh")

        # 创建界面
        self.create_widgets()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 设置字体 - 更大更舒适
        self.default_font = ("Microsoft YaHei", 12)  # 增大2号
        self.title_font = ("Microsoft YaHei", 14, "bold")  # 标题更大
        self.button_font = ("Microsoft YaHei", 11, "bold")  # 按钮字体
        self.result_font = ("Microsoft YaHei UI", 12)  # 转录结果用更舒适的字体
        self.small_font = ("Microsoft YaHei", 11)  # 小字体

        # 设置系统默认字体
        self.root.option_add("*Font", self.default_font)

        # 配置ttk样式
        style.configure("TLabel", font=self.default_font)
        style.configure("TLabelframe.Label", font=self.title_font)
        style.configure("TButton", font=self.button_font)
        style.configure("TCheckbutton", font=self.default_font)
        style.configure("TRadiobutton", font=self.default_font)
        style.configure("TCombobox", font=self.default_font)

    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=10)

        title_label = tk.Label(
            title_frame,
            text="🎤 Faster Whisper 实时转录",
            font=("Microsoft YaHei", 18, "bold"),  # 主标题更大
            bg='#f0f0f0',
            fg='#2196F3'
        )
        title_label.pack()

        # 创建主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左侧控制面板
        left_frame = tk.Frame(main_frame, bg='#f0f0f0', width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        # 右侧结果显示
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 创建控制面板
        self.create_control_panel(left_frame)

        # 创建结果显示面板
        self.create_result_panel(right_frame)

    def create_control_panel(self, parent):
        """创建控制面板"""
        # 文件选择
        file_frame = tk.LabelFrame(parent, text="📁 音频文件", bg='#f0f0f0', font=self.title_font)
        file_frame.pack(fill=tk.X, pady=8)

        file_entry = tk.Entry(file_frame, textvariable=self.file_var, width=35, font=self.default_font)
        file_entry.pack(padx=10, pady=8)

        browse_btn = tk.Button(
            file_frame,
            text="浏览文件...",
            command=self.browse_file,
            bg='#4CAF50',
            fg='white',
            font=self.button_font,
            padx=20,
            pady=8
        )
        browse_btn.pack(pady=8)

        # 模型选择
        model_frame = tk.LabelFrame(parent, text="🤖 模型设置", bg='#f0f0f0', font=self.title_font)
        model_frame.pack(fill=tk.X, pady=10)

        # 模型选择下拉框
        tk.Label(model_frame, text="选择转录模型:", bg='#f0f0f0', font=self.default_font).pack(anchor=tk.W, padx=10, pady=(12, 5))

        # 固定的模型选项
        self.model_var = tk.StringVar(value="whisper-large-v3-ct2")
        model_options = [
            "whisper-base-ct2 (基础模型，速度快)",
            "whisper-large-v3-ct2 (大型模型，精度高)"
        ]

        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=model_options,
            state="readonly",
            width=28,
            font=self.default_font
        )
        model_combo.pack(padx=10, pady=(5, 10))
        model_combo.bind("<<ComboboxSelected>>", self.on_model_selected)

        # 设备选择
        tk.Label(model_frame, text="计算设备:", bg='#f0f0f0', font=self.default_font).pack(anchor=tk.W, padx=10, pady=(12, 5))
        device_frame = tk.Frame(model_frame, bg='#f0f0f0')
        device_frame.pack(padx=10, pady=(0, 10))

        tk.Radiobutton(
            device_frame,
            text="CPU",
            variable=self.device_var,
            value="cpu",
            bg='#f0f0f0',
            font=self.default_font
        ).pack(side=tk.LEFT, padx=(0, 15))

        # 只有在有CUDA时才显示GPU选项
        if torch.cuda.is_available():
            tk.Radiobutton(
                device_frame,
                text="GPU (CUDA)",
                variable=self.device_var,
                value="cuda",
                bg='#f0f0f0',
                font=self.default_font
            ).pack(side=tk.LEFT)

        # 高级选项
        options_frame = tk.LabelFrame(parent, text="⚙️ 高级选项", bg='#f0f0f0', font=self.title_font)
        options_frame.pack(fill=tk.X, pady=10)

        tk.Checkbutton(
            options_frame,
            text="启用VAD语音活动检测",
            variable=self.vad_var,
            bg='#f0f0f0',
            anchor=tk.W,
            font=self.default_font
        ).pack(fill=tk.X, padx=10, pady=8)

        tk.Checkbutton(
            options_frame,
            text="显示词级时间戳",
            variable=self.word_timestamps_var,
            bg='#f0f0f0',
            anchor=tk.W,
            font=self.default_font
        ).pack(fill=tk.X, padx=10, pady=8)

        # 语言设置（固定为中文）
        lang_frame = tk.Frame(options_frame, bg='#f0f0f0')
        lang_frame.pack(fill=tk.X, padx=10, pady=(8, 12))

        tk.Label(lang_frame, text="语言: 中文", bg='#f0f0f0', font=self.default_font).pack(side=tk.LEFT)

        # 操作按钮
        button_frame = tk.Frame(parent, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=15)

        # 第一行主要操作按钮
        main_row = tk.Frame(button_frame, bg='#f0f0f0')
        main_row.pack(fill=tk.X, pady=(0, 8))

        self.start_btn = tk.Button(
            main_row,
            text="开始转录",
            command=self.start_transcription,
            bg='#2196F3',
            fg='white',
            font=self.button_font,
            padx=20,
            pady=10,
            width=12
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = tk.Button(
            main_row,
            text="停止",
            command=self.stop_transcription,
            bg='#f44336',
            fg='white',
            font=self.button_font,
            padx=20,
            pady=10,
            state=tk.DISABLED,
            width=8
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 8))

        # 第二行辅助按钮
        aux_row = tk.Frame(button_frame, bg='#f0f0f0')
        aux_row.pack(fill=tk.X)

        # 清空结果按钮
        clear_btn = tk.Button(
            aux_row,
            text="清空结果",
            command=self.clear_results,
            bg='#FF9800',
            fg='white',
            font=self.button_font,
            padx=15,
            pady=8,
            width=10
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 8))

        # 导出结果按钮
        export_btn = tk.Button(
            aux_row,
            text="导出文本",
            command=self.export_results,
            bg='#4CAF50',
            fg='white',
            font=self.button_font,
            padx=15,
            pady=8,
            width=10
        )
        export_btn.pack(side=tk.LEFT)

    def create_result_panel(self, parent):
        """创建结果显示面板"""
        result_frame = tk.LabelFrame(parent, text="📝 转录结果", bg='#f0f0f0', font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 状态栏
        status_frame = tk.Frame(result_frame, bg='#f0f0f0')
        status_frame.pack(fill=tk.X, padx=10, pady=8)

        self.status_label = tk.Label(
            status_frame,
            text="就绪",
            bg='#f0f0f0',
            fg='#666',
            font=self.default_font
        )
        self.status_label.pack(side=tk.LEFT)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            mode='indeterminate',
            length=150
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=10)

        # 文本结果显示区域
        text_frame = tk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # 创建滚动文本框 - 使用更舒适的字体和行距
        self.result_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=self.result_font,
            height=18,
            bg='#ffffff',
            fg='#333333',
            selectbackground='#2196F3',
            selectforeground='white',
            padx=8,
            pady=8,
            spacing1=4,  # 段落前间距
            spacing2=2,  # 段落中行间距
            spacing3=4   # 段落后间距
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 配置文本标签样式
        self.result_text.tag_configure("segment", lmargin1=10, lmargin2=20, font=self.result_font)
        self.result_text.tag_configure("timestamp", foreground='#666666', font=self.small_font)
        self.result_text.tag_configure("word", foreground='#2196F3', font=self.small_font)
        self.result_text.tag_configure("error", foreground='#f44336', font=self.default_font)

    def on_model_selected(self, event=None):
        """模型选择事件处理"""
        selected_model = self.model_var.get()
        # 提取纯模型名称用于显示
        if "whisper-base-ct2" in selected_model:
            model_name = "whisper-base-ct2"
        elif "whisper-large-v3-ct2" in selected_model:
            model_name = "whisper-large-v3-ct2"
        else:
            model_name = selected_model
        print(f"已选择模型: {model_name}")

  
    
    def browse_file(self):
        """浏览选择音频文件"""
        file_types = [
            ("音频文件", "*.mp3 *.wav *.m4a *.flac *.ogg"),
            ("MP3文件", "*.mp3"),
            ("WAV文件", "*.wav"),
            ("M4A文件", "*.m4a"),
            ("FLAC文件", "*.flac"),
            ("OGG文件", "*.ogg"),
            ("所有文件", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=file_types
        )

        if filename:
            self.file_var.set(filename)
            self.current_file = filename

    def start_transcription(self):
        """开始转录"""
        if not self.current_file:
            messagebox.showerror("错误", "请先选择音频文件")
            return

        if not os.path.exists(self.current_file):
            messagebox.showerror("错误", "文件不存在")
            return

        # 禁用开始按钮，启用停止按钮
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # 清空之前的结果
        self.result_text.delete(1.0, tk.END)

        # 开始进度条
        self.progress_bar.start()

        # 更新状态
        self.status_label.config(text="正在初始化模型...")

        # 在新线程中运行转录
        self.transcribing = True
        self.transcription_thread = threading.Thread(target=self.transcribe_worker)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()

    def transcribe_worker(self):
        """转录工作线程"""
        try:
            # 确保VAD模型可用
            ensure_vad_model()

            # 初始化模型
            model_path = self.get_model_path()

            def update_status(msg):
                self.root.after(0, lambda: self.status_label.config(text=msg))

            # 获取模型显示名称
            model_selection = self.model_var.get().strip()
            if model_selection:
                # 提取纯模型名称用于显示
                if "whisper-base-ct2" in model_selection:
                    model_name = "whisper-base-ct2"
                elif "whisper-large-v3-ct2" in model_selection:
                    model_name = "whisper-large-v3-ct2"
                else:
                    model_name = model_selection
                update_status(f"正在加载模型: {model_name}...")
            else:
                raise ValueError("请选择模型")

            # 确定计算类型
            device = self.device_var.get()
            if device == "cuda" and torch.cuda.is_available():
                compute_type = "int8"
            else:
                compute_type = "int8"
                device = "cpu"

            # 创建模型
            self.model = WhisperModel(
                model_path,
                device=device,
                compute_type=compute_type
            )

            update_status("正在转录音频...")

            # 准备转录参数
            transcribe_params = {
                "language": "zh",  # 强制使用中文
                "vad_filter": self.vad_var.get(),
                "word_timestamps": self.word_timestamps_var.get(),
                "beam_size": 5,
                "best_of": 5,
                "temperature": 0.0,
            }

            if self.vad_var.get():
                transcribe_params["vad_parameters"] = {"min_silence_duration_ms": 500}

            # 开始转录
            segments, info = self.model.transcribe(self.current_file, **transcribe_params)

            # 实时显示结果
            self.root.after(0, lambda: self.status_label.config(
                text=f"转录中 - 检测语言: {info.language} (置信度: {info.language_probability:.2%})"
            ))

            # 显示转录结果
            for i, segment in enumerate(segments):
                if not self.transcribing:
                    break

                # 在主线程中更新UI
                segment_data = {
                    'index': i + 1,
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip(),
                    'words': []
                }

                # 如果有词级时间戳
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        segment_data['words'].append({
                            'word': word.word,
                            'start': word.start,
                            'end': word.end,
                            'probability': word.probability
                        })

                # 在主线程中更新结果
                self.root.after(0, lambda sd=segment_data: self.display_segment(sd))

                # 短暂延迟以避免界面卡顿
                time.sleep(0.1)

            # 转录完成
            if self.transcribing:
                self.root.after(0, self.transcription_completed)

        except Exception as e:
            error_msg = f"转录失败: {str(e)}"
            self.root.after(0, lambda: self.transcription_error(error_msg))

    def get_model_path(self):
        """获取模型路径"""
        # 获取选择的模型名称
        model_selection = self.model_var.get().strip()
        if not model_selection:
            raise ValueError("请选择模型")

        # 从选项中提取模型名称（去除描述部分）
        if "whisper-base-ct2" in model_selection:
            model_name = "whisper-base-ct2"
        elif "whisper-large-v3-ct2" in model_selection:
            model_name = "whisper-large-v3-ct2"
        else:
            raise ValueError("无效的模型选择")

        # 构建模型完整路径
        model_path = os.path.join("models", model_name)

        if not Path(model_path).exists():
            raise FileNotFoundError(f"模型路径不存在: {model_path}")

        # 验证模型文件是否存在
        model_bin_path = os.path.join(model_path, "model.bin")
        if not Path(model_bin_path).exists():
            raise FileNotFoundError(f"模型文件不存在: {model_bin_path}")

        config_path = os.path.join(model_path, "config.json")
        if not Path(config_path).exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        return model_path

    def display_segment(self, segment_data):
        """显示转录片段"""
        # 添加时间戳和文本
        timestamp = f"[{format_time(segment_data['start'])} --> {format_time(segment_data['end'])}]"
        text = segment_data['text']

        # 插入时间戳
        self.result_text.insert(tk.END, f"{timestamp}\n", "timestamp")

        # 插入文本
        self.result_text.insert(tk.END, f"{text}\n\n", "segment")

        # 如果有词级时间戳，显示词汇详情
        if segment_data['words'] and self.word_timestamps_var.get():
            self.result_text.insert(tk.END, "  词汇详情:\n", "timestamp")
            for word in segment_data['words']:
                word_text = f"    {word['word']:.20s} [{format_time(word['start'])}]\n"
                self.result_text.insert(tk.END, word_text, "word")
            self.result_text.insert(tk.END, "\n")

        # 滚动到底部
        self.result_text.see(tk.END)
        self.result_text.update()

    def stop_transcription(self):
        """停止转录"""
        self.transcribing = False
        self.status_label.config(text="正在停止...")

        # 等待线程结束
        if self.transcription_thread and self.transcription_thread.is_alive():
            self.transcription_thread.join(timeout=2)

        self.transcription_finished()

    def transcription_completed(self):
        """转录完成"""
        self.transcribing = False
        self.status_label.config(text="转录完成 ✅")
        self.transcription_finished()

    def transcription_error(self, error_msg):
        """转录错误"""
        self.transcribing = False
        self.status_label.config(text=f"转录失败 ❌")
        self.result_text.insert(tk.END, f"\n❌ 错误: {error_msg}\n", "error")
        self.transcription_finished()
        messagebox.showerror("转录错误", error_msg)

    def transcription_finished(self):
        """转录结束后的清理工作"""
        self.progress_bar.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        # 清理模型
        if self.model:
            del self.model
            self.model = None

    def clear_results(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)
        self.status_label.config(text="结果已清空")

    def export_results(self):
        """导出转录结果到文本文件"""
        if not self.current_file:
            messagebox.showwarning("警告", "没有可导出的转录结果")
            return

        # 获取转录文本内容
        content = self.result_text.get(1.0, tk.END).strip()

        if not content or content == "":
            messagebox.showwarning("警告", "没有可导出的转录内容")
            return

        # 过滤掉时间戳，只保留转录文本
        pure_text = self.extract_text_only(content)

        if not pure_text.strip():
            messagebox.showwarning("警告", "没有有效的转录文本可导出")
            return

        # 生成默认文件名
        file_name = Path(self.current_file).stem
        default_name = f"{file_name}_转录文本.txt"

        # 打开文件保存对话框
        file_path = filedialog.asksaveasfilename(
            title="保存转录文本",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=default_name,
            initialdir=str(Path(self.current_file).parent)
        )

        if file_path:
            try:
                # 写入文件，使用UTF-8编码
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 写入标题信息
                    f.write(f"Faster Whisper 转录结果\n")
                    f.write(f"原始文件: {Path(self.current_file).name}\n")

                    # 获取模型显示名称
                    model_selection = self.model_var.get().strip()
                    if model_selection:
                        # 提取纯模型名称用于显示
                        if "whisper-base-ct2" in model_selection:
                            model_name = "whisper-base-ct2"
                        elif "whisper-large-v3-ct2" in model_selection:
                            model_name = "whisper-large-v3-ct2"
                        else:
                            model_name = model_selection
                        f.write(f"模型: {model_name}\n")
                    else:
                        f.write(f"模型: 未知\n")

                    f.write(f"导出时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")

                    # 写入纯文本内容
                    f.write(pure_text)

                messagebox.showinfo("成功", f"转录文本已保存到:\n{file_path}")
                self.status_label.config(text=f"已导出到: {Path(file_path).name}")

            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败:\n{str(e)}")

    def extract_text_only(self, content):
        """从转录结果中提取纯文本，去除时间戳和其他标记"""
        lines = content.split('\n')
        pure_text_lines = []

        for line in lines:
            line = line.strip()

            # 跳过时间戳行（格式如: [00:00:00.000 --> 00:00:05.000]）
            if line.startswith('[') and '-->' in line and line.endswith(']'):
                continue

            # 跳过空行
            if not line:
                continue

            # 跳过词汇详情行
            if line.startswith('  词汇详情:') or line.startswith('    '):
                continue

            # 跳过其他标记行
            if line.startswith('转录中 - 检测语言:') or line.startswith('❌ 错误:'):
                continue

            # 添加有效文本行
            pure_text_lines.append(line)

        # 合并文本，添加适当的段落分隔
        return '\n\n'.join(pure_text_lines)

    def run(self):
        """运行应用"""
        # 处理窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """窗口关闭事件处理"""
        if self.transcribing:
            if messagebox.askokcancel("退出", "转录正在进行中，确定要退出吗？"):
                self.transcribing = False
                if self.transcription_thread and self.transcription_thread.is_alive():
                    self.transcription_thread.join(timeout=1)
                self.root.destroy()
        else:
            self.root.destroy()


def format_time(seconds):
    """格式化时间显示"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"
    else:
        return f"{minutes:02d}:{secs:02d}.{ms:03d}"


def main():
    """主函数"""
    # 检查CUDA可用性
    print(f"CUDA 可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA 设备: {torch.cuda.get_device_name(0)}")

    # 启动GUI
    app = WhisperGUI()
    app.run()


if __name__ == "__main__":
    main()