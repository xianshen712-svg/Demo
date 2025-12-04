import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from collections import deque
import os
from scipy import signal
from tkinter import filedialog
import re
from tkinter import messagebox
import time
import threading

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class OpenBCIInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Acl-EM 脑电监测系统")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # 配置参数
        self.sample_rate = 250
        self.display_duration = 10
        self.buffer_size = self.sample_rate * self.display_duration
        
        # 数据缓冲区
        self.eeg_data = None
        self.current_index = 0
        self.streaming = False
        self.data_thread = None
        self.update_interval = 50
        
        # 图表窗口相关
        self.chart_windows = {}
        self.chart_figures = {}
        self.chart_canvases = {}
        
        # 初始化所有必要的属性
        self.rms_texts = []
        self.time_lines = []
        self.axes_time = []
        self.data_buffers = []
        self.electrodes = []
        self.focus_bars = []
        
        # 初始化界面
        self.setup_interface()
        self.setup_data_buffers()
        
    def setup_interface(self):
        """设置主界面布局 - 模仿图片样式"""
        # 顶部标题栏
        self.setup_title_bar()
        
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 左侧导航栏
        self.setup_left_navigation(main_container)
        
        # 右侧内容区域
        right_container = tk.Frame(main_container, bg='white')
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部控制栏（包含四个图表按钮）
        self.setup_top_control_bar(right_container)
        
        # 主显示区域（显示时间序列和头部地形图）
        self.setup_main_display_area(right_container)
        
    def setup_title_bar(self):
        """设置顶部标题栏 - 模仿图片样式"""
        title_bar = tk.Frame(self.root, bg='#2c80c8', height=40)
        title_bar.pack(fill=tk.X, padx=0, pady=0)
        title_bar.pack_propagate(False)
        
        # 软件标题
        title_label = tk.Label(title_bar, text="Acl-EM 脑电监测系统", 
                              font=('微软雅黑', 16, 'bold'), 
                              bg='#2c80c8', fg='white')
        title_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # 状态信息
        self.status_label = tk.Label(title_bar, text="准备就绪", 
                                   font=('微软雅黑', 12), 
                                   bg='#2c80c8', fg='white')
        self.status_label.pack(side=tk.RIGHT, padx=15, pady=8)
        
    def setup_left_navigation(self, parent):
        """设置左侧导航栏 - 模仿图片样式"""
        nav_frame = tk.Frame(parent, bg='#e8e8e8', width=120)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        nav_frame.pack_propagate(False)
        
        # 导航按钮 - 模仿图片的灰色长方形按钮
        nav_buttons = [
            ("脑电监测", self.show_eeg_monitor),
            ("快速评估", self.show_quick_assessment),
            ("量表评估", self.show_scale_assessment),
            ("系统设置", self.show_system_settings),
            ("患者管理", self.show_patient_management)
        ]
        
        # 按钮样式配置
        button_style = {
            'bg': '#e0e0e0',
            'fg': '#000000',
            'font': ('微软雅黑', 11, 'bold'),
            'relief': 'raised',
            'bd': 2,
            'width': 12,
            'height': 2
        }
        
        for i, (text, command) in enumerate(nav_buttons):
            btn = tk.Button(nav_frame, text=text, command=command, **button_style)
            btn.pack(fill=tk.X, padx=10, pady=8)
            
            # 设置第一个按钮为选中状态
            if i == 0:
                btn.configure(bg='#d0d0d0')
                self.current_nav_button = btn
        
    def setup_top_control_bar(self, parent):
        """设置顶部控制栏 - 包含四个图表按钮"""
        control_bar = tk.Frame(parent, bg='#f5f5f5', height=60)
        control_bar.pack(fill=tk.X, padx=10, pady=10)
        control_bar.pack_propagate(False)
        
        # 控制按钮容器
        button_frame = tk.Frame(control_bar, bg='#f5f5f5')
        button_frame.pack(expand=True, fill=tk.X, padx=20, pady=10)
        
        # 基本控制按钮
        basic_buttons = [
            ("加载数据文件", self.load_data_file),
            ("开始数据流", self.start_stream),
            ("停止数据流", self.stop_stream),
            ("重置显示", self.reset_display)
        ]
        
        # 基本按钮样式
        btn_style = {
            'font': ('微软雅黑', 10),
            'relief': 'raised',
            'bd': 1,
            'width': 12,
            'height': 1
        }
        
        # 添加基本按钮
        for text, command in basic_buttons:
            btn = tk.Button(button_frame, text=text, command=command, **btn_style)
            btn.pack(side=tk.LEFT, padx=5)
        
        # 图表按钮容器
        chart_button_frame = tk.Frame(button_frame, bg='#f5f5f5')
        chart_button_frame.pack(side=tk.LEFT, padx=20)
        
        # 四个图表按钮 - 模仿图片样式
        chart_buttons = [
            ("时间序列", self.show_time_series_chart, '#3498db'),
            ("头部地形图", self.show_head_plot_chart, '#e74c3c'),
            ("频谱分析", self.show_fft_chart, '#2ecc71'),
            ("专注度", self.show_focus_chart, '#f39c12')
        ]
        
        # 图表按钮样式
        chart_btn_style = {
            'font': ('微软雅黑', 10, 'bold'),
            'relief': 'raised',
            'bd': 2,
            'width': 10,
            'height': 1
        }
        
        for text, command, color in chart_buttons:
            btn = tk.Button(chart_button_frame, text=text, command=command,
                          bg=color, fg='white', **chart_btn_style)
            btn.pack(side=tk.LEFT, padx=3)
            btn.configure(activebackground=color, activeforeground='white')
        
        # 滤波器设置
        filter_frame = tk.Frame(button_frame, bg='#f5f5f5')
        filter_frame.pack(side=tk.RIGHT, padx=10)
        
        self.notch_var = tk.BooleanVar()
        notch_cb = tk.Checkbutton(filter_frame, text="陷波滤波器 60Hz", 
                                 variable=self.notch_var,
                                 font=('微软雅黑', 9), bg='#f5f5f5')
        notch_cb.pack(side=tk.LEFT, padx=5)
        
        self.bp_var = tk.BooleanVar()
        bp_cb = tk.Checkbutton(filter_frame, text="带通滤波器 5-50Hz", 
                              variable=self.bp_var,
                              font=('微软雅黑', 9), bg='#f5f5f5')
        bp_cb.pack(side=tk.LEFT, padx=5)
        
    def setup_main_display_area(self, parent):
        """设置主显示区域 - 显示时间序列和头部地形图"""
        display_frame = tk.Frame(parent, bg='white')
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 配置网格布局
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_columnconfigure(1, weight=1)
        
        # 左侧：时间序列波形
        time_frame = ttk.LabelFrame(display_frame, text="脑电信号时间序列 - 8通道分离显示", padding=5)
        time_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        time_frame.grid_rowconfigure(0, weight=1)
        time_frame.grid_columnconfigure(0, weight=1)
        self.setup_time_series(time_frame)
        
        # 右侧：头部地形图
        head_frame = ttk.LabelFrame(display_frame, text="脑电活动地形图", padding=5)
        head_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        head_frame.grid_rowconfigure(0, weight=1)
        head_frame.grid_columnconfigure(0, weight=1)
        self.setup_head_plot(head_frame)
        
    def setup_time_series(self, parent):
        """设置时间序列波形显示"""
        # 确保属性已初始化
        if not hasattr(self, 'rms_texts'):
            self.rms_texts = []
        if not hasattr(self, 'time_lines'):
            self.time_lines = []
        if not hasattr(self, 'axes_time'):
            self.axes_time = []
            
        # 清空现有列表
        self.axes_time.clear()
        self.time_lines.clear()
        self.rms_texts.clear()
        
        # 创建图形
        self.fig_time = Figure(figsize=(10, 8), dpi=100)
        
        # 通道颜色配置
        self.channel_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
            '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
        ]
        
        # 创建8个独立的子图
        for i in range(8):
            ax = self.fig_time.add_subplot(8, 1, i+1)
            self.axes_time.append(ax)
            
            # 设置每个通道的子图样式
            ax.set_facecolor('white')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(-self.display_duration, 0)
            ax.set_ylim(-200, 200)
            
            # Y轴标签
            ax.set_ylabel(f'通道{i+1}', rotation=0, ha='right', va='center', 
                         fontsize=10, fontweight='bold', labelpad=15)
            
            if i < 7:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel('时间 (秒)', fontsize=10)
            
            # 创建波形线
            line, = ax.plot([], [], color=self.channel_colors[i], linewidth=1.5)
            self.time_lines.append(line)
            
            # 添加RMS值显示
            rms_text = ax.text(0.98, 0.95, '0.00 uVrms', 
                              transform=ax.transAxes, fontsize=9,
                              bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                              ha='right', va='top')
            self.rms_texts.append(rms_text)
        
        self.fig_time.suptitle('脑电信号时间序列', fontsize=12, fontweight='bold')
        self.fig_time.tight_layout()
        self.fig_time.subplots_adjust(top=0.95, hspace=0.4)
        
        # 嵌入到Tkinter
        self.canvas_time = FigureCanvasTkAgg(self.fig_time, parent)
        self.canvas_time.draw()
        self.canvas_time.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_head_plot(self, parent):
        """设置头部地形图显示"""
        self.fig_head = Figure(figsize=(6, 6), dpi=100)
        self.ax_head = self.fig_head.add_subplot(111)
        
        self.ax_head.set_xlim(-1.2, 1.2)
        self.ax_head.set_ylim(-1.2, 1.2)
        self.ax_head.set_aspect('equal')
        self.ax_head.axis('off')
        self.ax_head.set_title('脑电活动地形图', fontsize=12, fontweight='bold')
        
        # 绘制头部轮廓
        head_circle = plt.Circle((0, 0), 1, fill=False, color='black', linewidth=2)
        self.ax_head.add_patch(head_circle)
        
        # 电极位置
        electrode_positions = [
            (0, 0.8), (-0.5, 0.5), (0.5, 0.5), (-0.8, 0), 
            (0.8, 0), (-0.5, -0.5), (0.5, -0.5), (0, -0.8)
        ]
        
        self.electrodes = []
        for i, (x, y) in enumerate(electrode_positions):
            electrode = plt.Circle((x, y), 0.08, color=self.channel_colors[i], alpha=0.7)
            self.ax_head.add_patch(electrode)
            self.ax_head.text(x, y, str(i+1), ha='center', va='center', 
                            fontsize=8, fontweight='bold')
            self.electrodes.append(electrode)
        
        self.canvas_head = FigureCanvasTkAgg(self.fig_head, parent)
        self.canvas_head.draw()
        self.canvas_head.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_data_buffers(self):
        """初始化数据缓冲区"""
        self.time_buffer = deque([-self.display_duration + i/self.sample_rate 
                                for i in range(self.buffer_size)], maxlen=self.buffer_size)
        
        self.data_buffers = []
        for i in range(8):
            buffer = deque([0] * self.buffer_size, maxlen=self.buffer_size)
            self.data_buffers.append(buffer)
    
    # 图表窗口功能
    def show_time_series_chart(self):
        """显示时间序列图表窗口"""
        if 'time_series' not in self.chart_windows or not self.chart_windows['time_series'].winfo_exists():
            self.create_chart_window('time_series', '脑电信号时间序列', self.create_time_series_chart)
        else:
            self.chart_windows['time_series'].lift()
            
    def show_head_plot_chart(self):
        """显示头部地形图图表窗口"""
        if 'head_plot' not in self.chart_windows or not self.chart_windows['head_plot'].winfo_exists():
            self.create_chart_window('head_plot', '脑电活动地形图', self.create_head_plot_chart)
        else:
            self.chart_windows['head_plot'].lift()
            
    def show_fft_chart(self):
        """显示FFT频谱图表窗口"""
        if 'fft' not in self.chart_windows or not self.chart_windows['fft'].winfo_exists():
            self.create_chart_window('fft', '功率谱密度', self.create_fft_chart)
        else:
            self.chart_windows['fft'].lift()
            
    def show_focus_chart(self):
        """显示专注度图表窗口"""
        if 'focus' not in self.chart_windows or not self.chart_windows['focus'].winfo_exists():
            self.create_chart_window('focus', '脑电频带功率分布', self.create_focus_chart)
        else:
            self.chart_windows['focus'].lift()
    
    def create_chart_window(self, chart_type, title, create_function):
        """创建图表窗口"""
        # 创建新窗口
        chart_window = tk.Toplevel(self.root)
        chart_window.title(title)
        chart_window.geometry("800x600")
        chart_window.configure(bg='white')
        
        # 存储窗口引用
        self.chart_windows[chart_type] = chart_window
        
        # 创建图表
        fig = Figure(figsize=(8, 6), dpi=100)
        canvas = FigureCanvasTkAgg(fig, chart_window)
        
        # 调用创建函数
        create_function(fig, canvas)
        
        # 存储图表和画布
        self.chart_figures[chart_type] = fig
        self.chart_canvases[chart_type] = canvas
        
        # 布局
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 窗口关闭事件
        chart_window.protocol("WM_DELETE_WINDOW", lambda: self.close_chart_window(chart_type))
        
        # 如果数据流正在运行，开始更新图表
        if self.streaming:
            self.start_chart_updates(chart_type)
    
    def close_chart_window(self, chart_type):
        """关闭图表窗口"""
        if chart_type in self.chart_windows:
            self.chart_windows[chart_type].destroy()
            del self.chart_windows[chart_type]
            if chart_type in self.chart_figures:
                del self.chart_figures[chart_type]
            if chart_type in self.chart_canvases:
                del self.chart_canvases[chart_type]
    
    def create_time_series_chart(self, fig, canvas):
        """创建时间序列图表"""
        # 清空图形
        fig.clf()
        
        # 创建8个子图
        axes = []
        lines = []
        
        for i in range(8):
            ax = fig.add_subplot(8, 1, i+1)
            axes.append(ax)
            
            # 设置样式
            ax.set_facecolor('white')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(-self.display_duration, 0)
            ax.set_ylim(-200, 200)
            
            # Y轴标签
            ax.set_ylabel(f'通道{i+1}', rotation=0, ha='right', va='center', 
                         fontsize=10, fontweight='bold', labelpad=15)
            
            if i < 7:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel('时间 (秒)', fontsize=10)
            
            # 创建波形线
            line, = ax.plot([], [], color=self.channel_colors[i], linewidth=1.5)
            lines.append(line)
        
        fig.suptitle('脑电信号时间序列', fontsize=12, fontweight='bold')
        fig.tight_layout()
        fig.subplots_adjust(top=0.95, hspace=0.4)
        
        # 存储图表元素
        self.chart_time_axes = axes
        self.chart_time_lines = lines
        
        canvas.draw()
    
    def create_head_plot_chart(self, fig, canvas):
        """创建头部地形图图表"""
        fig.clf()
        ax = fig.add_subplot(111)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('脑电活动地形图', fontsize=12, fontweight='bold')
        
        # 绘制头部轮廓
        head_circle = plt.Circle((0, 0), 1, fill=False, color='black', linewidth=2)
        ax.add_patch(head_circle)
        
        # 电极位置
        electrode_positions = [
            (0, 0.8), (-0.5, 0.5), (0.5, 0.5), (-0.8, 0), 
            (0.8, 0), (-0.5, -0.5), (0.5, -0.5), (0, -0.8)
        ]
        
        electrodes = []
        for i, (x, y) in enumerate(electrode_positions):
            electrode = plt.Circle((x, y), 0.08, color=self.channel_colors[i], alpha=0.7)
            ax.add_patch(electrode)
            ax.text(x, y, str(i+1), ha='center', va='center', 
                   fontsize=8, fontweight='bold')
            electrodes.append(electrode)
        
        # 存储电极引用
        self.chart_electrodes = electrodes
        
        canvas.draw()
    
    def create_fft_chart(self, fig, canvas):
        """创建FFT频谱图表 - 完全匹配图片样式"""
        fig.clf()
        ax = fig.add_subplot(111)
        
        # 设置图表样式（完全匹配图片）
        ax.set_facecolor('white')
        fig.set_facecolor('white')
        
        # 设置坐标轴范围
        ax.set_xlim(0, 50)  # 横轴：0-50Hz
        ax.set_ylim(0, 10)  # 纵轴：10⁰-10¹（线性显示）
        
        # 标题和标签
        ax.set_title('功率谱密度', fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel('频率 (Hz)', fontsize=10)
        ax.set_ylabel('功率 (dB)', fontsize=10)
        
        # 网格线
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # 坐标轴样式（黑色边框）
        ax.tick_params(colors='black')
        for spine in ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(1)
        
        # 创建空的频谱线（红色）
        fft_line, = ax.plot([], [], 'r-', linewidth=1.5)
        
        # 存储图表元素引用
        self.chart_fft_line = fft_line
        self.chart_fft_ax = ax
        self.chart_figures['fft'] = fig
        
        canvas.draw()

    
    def create_focus_chart(self, fig, canvas):
        """创建专注度图表"""
        fig.clf()
        ax = fig.add_subplot(111)
        
        ax.set_title('脑电频带功率分布')
        ax.set_ylabel('功率百分比 (%)')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        # 创建专注度条形图
        bands = ['Delta波', 'Theta波', 'Alpha波', 'Beta波']
        focus_bars = ax.bar(bands, [0, 0, 0, 0], 
                          color=['red', 'purple', 'blue', 'green'])
        
        ax.set_xticklabels(bands, rotation=45)
        
        # 存储条形图引用
        self.chart_focus_bars = focus_bars
        self.chart_focus_ax = ax
        
        canvas.draw()
    
    def start_chart_updates(self, chart_type):
        """开始图表更新"""
        if chart_type in self.chart_windows and self.chart_windows[chart_type].winfo_exists():
            if self.streaming:
                self.update_chart(chart_type)
                self.root.after(self.update_interval, 
                              lambda: self.start_chart_updates(chart_type))
    
    def update_chart(self, chart_type):
        """更新指定类型的图表"""
        if chart_type not in self.chart_windows or not self.chart_windows[chart_type].winfo_exists():
            return
        
        try:
            if chart_type == 'time_series' and hasattr(self, 'chart_time_lines'):
                self.update_time_series_chart()
            elif chart_type == 'head_plot' and hasattr(self, 'chart_electrodes'):
                self.update_head_plot_chart()
            elif chart_type == 'fft' and hasattr(self, 'chart_fft_line'):
                self.update_fft_chart()
            elif chart_type == 'focus' and hasattr(self, 'chart_focus_bars'):
                self.update_focus_chart()
        except Exception as e:
            print(f"更新图表 {chart_type} 错误: {e}")
    
    def update_time_series_chart(self):
        """更新时间序列图表"""
        time_array = np.array(self.time_buffer)
        
        for ch in range(8):
            if ch < len(self.data_buffers) and ch < len(self.chart_time_lines):
                data_array = np.array(self.data_buffers[ch])
                self.chart_time_lines[ch].set_data(time_array, data_array)
                
                # 自动调整Y轴范围
                if len(data_array) > 0:
                    y_range = max(50, np.max(np.abs(data_array)) * 1.2)
                    self.chart_time_axes[ch].set_ylim(-y_range, y_range)
        
        self.chart_canvases['time_series'].draw()
    
    def update_head_plot_chart(self):
        """更新头部地形图图表"""
        for i, electrode in enumerate(self.chart_electrodes):
            if i < len(self.data_buffers) and len(self.data_buffers[i]) > 0:
                latest_value = self.data_buffers[i][-1]
                intensity = min(1.0, abs(latest_value) / 100)
                electrode.set_alpha(0.3 + 0.7 * intensity)
        
        self.chart_canvases['head_plot'].draw()
    
    def update_fft_chart(self):
        """更新FFT频谱图表 - 完全匹配图片样式"""
        if len(self.data_buffers[0]) > 100:
            try:
                # 获取数据（使用通道1的数据）
                data = np.array(self.data_buffers[0])
                
                # 只使用最近的数据点提高性能
                if len(data) > 512:
                    data = data[-512:]
                
                # 计算功率谱密度
                f, Pxx = signal.welch(data, self.sample_rate, nperseg=256, scaling='density')
                
                # 转换为dB单位（匹配图片的纵轴）
                Pxx_db = 10 * np.log10(Pxx + 1e-12)  # 加小值避免log(0)
                
                # 应用滤波器设置
                if self.notch_var.get():
                    notch_freq = 60
                    notch_width = 5
                    mask = (f > notch_freq - notch_width) & (f < notch_freq + notch_width)
                    Pxx_db[mask] = np.min(Pxx_db)  # 将陷波频率区域的功率设为最小值
                
                if self.bp_var.get():
                    # 带通滤波：只保留5-50Hz
                    mask = (f >= 5) & (f <= 50)
                    if np.any(mask):
                        # 只显示带通范围内的数据，其他区域设为最小值
                        min_val = np.min(Pxx_db)
                        Pxx_db[~mask] = min_val
                
                # 更新图表数据
                self.chart_fft_line.set_data(f, Pxx_db)
                
                # 设置固定的坐标轴范围（完全匹配图片）
                self.chart_fft_ax.set_xlim(0, 50)  # 横轴：0-50Hz
                self.chart_fft_ax.set_ylim(0, 10)  # 纵轴：10⁰-10¹（线性显示，因为已经转换为dB）
                
                # 确保使用线性坐标（图片显示的是线性坐标，不是对数坐标）
                self.chart_fft_ax.set_yscale('linear')
                
                # 设置网格和样式（匹配图片）
                self.chart_fft_ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                
                # 设置标题和标签样式
                self.chart_fft_ax.set_title('功率谱密度', fontsize=12, fontweight='bold', pad=10)
                self.chart_fft_ax.set_xlabel('频率 (Hz)', fontsize=10)
                self.chart_fft_ax.set_ylabel('功率 (dB)', fontsize=10)
                
                # 设置坐标轴颜色和边框（黑色边框）
                self.chart_fft_ax.tick_params(colors='black')
                for spine in self.chart_fft_ax.spines.values():
                    spine.set_color('black')
                    spine.set_linewidth(1)
                
                # 设置背景色为白色
                self.chart_fft_ax.set_facecolor('white')
                self.chart_figures['fft'].set_facecolor('white')
                
                # 重绘图表
                self.chart_canvases['fft'].draw()
                
                # 调试信息
                if hasattr(self, 'debug_fft') and self.debug_fft:
                    if len(Pxx_db) > 0:
                        valid_data = Pxx_db[Pxx_db > -100]  # 过滤无效值
                        if len(valid_data) > 0:
                            print(f"FFT更新: 频率点{len(f)}, 功率范围[{np.min(valid_data):.1f}, {np.max(valid_data):.1f}] dB")
                    
            except Exception as e:
                print(f"FFT图表更新错误: {e}")
                # 显示错误状态
                self.chart_fft_ax.set_title('功率谱密度 - 计算错误', color='red')
                self.chart_canvases['fft'].draw()
    
    def update_focus_chart(self):
        """更新专注度图表"""
        if len(self.data_buffers[0]) > 100:
            try:
                data = np.array(self.data_buffers[0])
                f, Pxx = signal.welch(data, self.sample_rate, nperseg=256)
                
                # 计算频带功率
                delta_power = np.mean(Pxx[(f >= 1) & (f <= 4)])
                theta_power = np.mean(Pxx[(f >= 4) & (f <= 8)])
                alpha_power = np.mean(Pxx[(f >= 8) & (f <= 13)])
                beta_power = np.mean(Pxx[(f >= 13) & (f <= 30)])
                
                powers = [delta_power, theta_power, alpha_power, beta_power]
                total_power = sum(powers) if sum(powers) > 0 else 1
                
                # 更新条形图
                for i, (bar, power) in enumerate(zip(self.chart_focus_bars, powers)):
                    height = (power / total_power) * 100
                    bar.set_height(height)
                
                self.chart_canvases['focus'].draw()
                
            except Exception as e:
                print(f"专注度图表更新错误: {e}")
    
    # 数据流控制功能
    def load_data_file(self):
        """加载数据文件"""
        try:
            filepath = filedialog.askopenfilename(
                title="选择OpenBCI数据文件",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            
            if not filepath:
                return
                
            print(f"正在加载文件: {filepath}")
            
            # 使用健壮的数据读取方法
            self.eeg_data = self.robust_read_openbci_file(filepath)
            
            if self.eeg_data is not None:
                filename = os.path.basename(filepath)
                self.status_label.config(text=f"已加载: {filename}")
                self.current_index = 0
                print(f"✅ 数据加载成功! 形状: {self.eeg_data.shape}")
                messagebox.showinfo("成功", f"数据加载成功!\n文件: {filename}\n数据点数: {len(self.eeg_data)}")
            else:
                self.status_label.config(text="加载数据失败")
                if messagebox.askyesno("数据加载失败", "是否使用模拟数据进行演示？"):
                    self.create_sample_data()
                    
        except Exception as e:
            error_msg = f"加载文件时出错: {str(e)}"
            self.status_label.config(text=error_msg)
            messagebox.showerror("错误", error_msg)
    
    def robust_read_openbci_file(self, filepath):
        """健壮的OpenBCI文件读取函数"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            data_lines = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('%') or line.startswith('#'):
                    continue
                
                # 尝试多种分隔符
                for sep in [',', '\t', ' ']:
                    if sep in line:
                        parts = [p.strip() for p in line.split(sep) if p.strip()]
                        if len(parts) >= 8:
                            try:
                                # 提取数值数据
                                numeric_data = []
                                for part in parts:
                                    try:
                                        # 处理科学计数法
                                        if 'e' in part.lower() or 'E' in part:
                                            numeric_data.append(float(part))
                                        else:
                                            # 清理非数字字符
                                            clean_part = re.sub(r'[^\d.-]', '', part)
                                            if clean_part:
                                                numeric_data.append(float(clean_part))
                                    except:
                                        continue
                                
                                if len(numeric_data) >= 8:
                                    data_lines.append(numeric_data[:8])
                                    break
                            except:
                                continue
            
            if data_lines:
                data_array = np.array(data_lines)
                print(f"✅ 成功读取 {len(data_array)} 行数据")
                return data_array
            return None
                
        except Exception as e:
            print(f"❌ 读取文件错误: {e}")
            return None
    
    def create_sample_data(self):
        """创建样本数据用于演示"""
        print("创建模拟EEG数据用于演示...")
        duration = 30  # 30秒数据
        n_samples = self.sample_rate * duration
        t = np.linspace(0, duration, n_samples)
        
        # 生成8通道模拟EEG数据
        self.eeg_data = np.zeros((n_samples, 8))
        frequencies = [10, 20, 6, 15, 25, 8, 12, 18]
        
        for ch in range(8):
            # 基础脑电波 + 噪声 + 事件
            base_signal = 20 * np.sin(2 * np.pi * frequencies[ch] * t)
            noise = np.random.normal(0, 3, n_samples)
            envelope = np.exp(-0.005 * t)
            
            # 添加模拟事件
            events = np.zeros_like(t)
            for event_time in [5, 15, 25]:
                event_mask = (t >= event_time) & (t < event_time + 2)
                events[event_mask] = 10 * np.sin(2 * np.pi * 3 * (t[event_mask] - event_time))
            
            self.eeg_data[:, ch] = base_signal * envelope + noise + events
        
        self.status_label.config(text="使用模拟数据演示")
        self.current_index = 0
        print("✅ 模拟数据生成完成")
        messagebox.showinfo("信息", "正在使用模拟数据进行演示")
    
    def start_stream(self):
        """开始数据流"""
        if self.eeg_data is None:
            if messagebox.askyesno("未加载数据", "是否使用模拟数据进行演示？"):
                self.create_sample_data()
            else:
                return
        
        if self.streaming:
            self.status_label.config(text="数据流已在运行")
            return
        
        self.streaming = True
        self.status_label.config(text="数据流传输中...")
        
        # 启动数据流线程
        self.data_thread = threading.Thread(target=self.data_stream_worker, daemon=True)
        self.data_thread.start()
        
        # 开始界面更新
        self.update_display()
        
        # 启动所有打开的图表窗口的更新
        for chart_type in self.chart_windows.keys():
            if self.chart_windows[chart_type].winfo_exists():
                self.start_chart_updates(chart_type)
    
    def data_stream_worker(self):
        """数据流工作线程"""
        while self.streaming:
            try:
                # 每次添加新数据点
                samples_to_add = min(5, len(self.eeg_data) - self.current_index)
                
                for _ in range(samples_to_add):
                    if self.current_index < len(self.eeg_data):
                        for ch in range(8):
                            if ch < self.eeg_data.shape[1]:
                                self.data_buffers[ch].append(self.eeg_data[self.current_index, ch])
                            else:
                                self.data_buffers[ch].append(0)
                        self.current_index += 1
                    else:
                        # 数据播放完毕，循环播放
                        self.current_index = 0
                
                time.sleep(self.update_interval / 1000)
                
            except Exception as e:
                print(f"数据流错误: {e}")
                break
    
    def stop_stream(self):
        """停止数据流"""
        self.streaming = False
        self.status_label.config(text="已停止")
        
        if self.data_thread and self.data_thread.is_alive():
            self.data_thread.join(timeout=1.0)
    
    def reset_display(self):
        """重置显示"""
        self.current_index = 0
        self.setup_data_buffers()
        self.update_display()
        self.status_label.config(text="已重置")
    
    def update_display(self):
        """更新主界面显示"""
        if not self.streaming:
            return
        
        try:
            # 更新时间序列
            self.update_time_series()
            
            # 更新头部地形图
            self.update_head_plot()
            
            # 继续更新
            if self.streaming:
                self.root.after(self.update_interval, self.update_display)
                
        except Exception as e:
            print(f"更新显示错误: {e}")
            self.streaming = False
    
    def update_time_series(self):
        """更新时间序列显示"""
        time_array = np.array(self.time_buffer)
        
        for ch in range(8):
            data_array = np.array(self.data_buffers[ch])
            self.time_lines[ch].set_data(time_array, data_array)
            
            # 自动调整Y轴范围
            if len(data_array) > 0:
                y_range = max(50, np.max(np.abs(data_array)) * 1.2)
                self.axes_time[ch].set_ylim(-y_range, y_range)
            
            # 更新RMS值
            if len(data_array) > 0:
                rms_value = np.sqrt(np.mean(data_array ** 2))
                self.rms_texts[ch].set_text(f'{rms_value:.2f} uVrms')
        
        self.canvas_time.draw()
    
    def update_head_plot(self):
        """更新头部地形图显示"""
        for i, electrode in enumerate(self.electrodes):
            if i < len(self.data_buffers) and len(self.data_buffers[i]) > 0:
                latest_value = self.data_buffers[i][-1]
                intensity = min(1.0, abs(latest_value) / 100)
                electrode.set_alpha(0.3 + 0.7 * intensity)
        
        self.canvas_head.draw()
    
    # 导航按钮功能
    def show_eeg_monitor(self):
        """显示脑电监测页面"""
        self.update_navigation_button("脑电监测")
        self.status_label.config(text="脑电监测模式")
        
    def show_quick_assessment(self):
        """显示快速评估页面"""
        self.update_navigation_button("快速评估")
        self.status_label.config(text="快速评估模式")
        
    def show_scale_assessment(self):
        """显示量表评估页面"""
        self.update_navigation_button("量表评估")
        self.status_label.config(text="量表评估模式")
        
    def show_system_settings(self):
        """显示系统设置页面"""
        self.update_navigation_button("系统设置")
        self.status_label.config(text="系统设置模式")
        
    def show_patient_management(self):
        """显示患者管理页面"""
        self.update_navigation_button("患者管理")
        self.status_label.config(text="患者管理模式")
        
    def update_navigation_button(self, selected_text):
        """更新导航按钮选中状态"""
        # 重置所有按钮颜色
        for widget in self.current_nav_button.master.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg='#e0e0e0')
        
        # 设置选中按钮颜色
        for widget in self.current_nav_button.master.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget('text') == selected_text:
                widget.configure(bg='#d0d0d0')
                self.current_nav_button = widget
                break

def main():
    """主函数"""
    root = tk.Tk()
    app = OpenBCIInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()