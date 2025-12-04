import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import pandas as pd
import os
import time

class EEGWaveformPlotter:
    def __init__(self, sample_rate=250, display_duration=10):
        """
        EEG波形显示器
        参数:
        sample_rate: 采样率 (Hz), OpenBCI默认250Hz
        display_duration: 显示时间窗口 (秒)
        """
        self.sample_rate = sample_rate
        self.display_duration = display_duration
        self.buffer_size = sample_rate * display_duration
        
        # 通道配置
        self.channel_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                             '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        # 数据缓冲区
        self.data_buffers = [deque([0]*self.buffer_size, maxlen=self.buffer_size) 
                            for _ in range(8)]
        self.time_buffer = deque([-self.display_duration + i/self.sample_rate 
                                 for i in range(self.buffer_size)], maxlen=self.buffer_size)
        
        self.setup_plot()
    
    def setup_plot(self):
        """设置8通道波形显示界面"""
        self.fig, self.axes = plt.subplots(8, 1, figsize=(12, 8))
        plt.subplots_adjust(hspace=0.3)
        
        # 设置每个通道的子图
        for i, ax in enumerate(self.axes):
            ax.set_facecolor('#f8f9fa')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(-self.display_duration, 0)
            ax.set_ylim(-100, 100)
            
            # Y轴标签（通道编号）
            ax.set_ylabel(f'Ch{i+1}', rotation=0, ha='right', va='center', 
                         fontsize=10, fontweight='bold', labelpad=20)
            
            # 移除不必要的刻度标签
            if i < 7:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel('Time (s)', fontsize=12)
        
        self.fig.suptitle('OpenBCI EEG Waveform - Time Series', 
                         fontsize=14, fontweight='bold')
        
        # 创建波形线
        self.lines = []
        for i, ax in enumerate(self.axes):
            line, = ax.plot([], [], color=self.channel_colors[i], linewidth=1.2)
            self.lines.append(line)
        
        # RMS值显示
        self.rms_texts = []
        for i, ax in enumerate(self.axes):
            text = ax.text(0.98, 0.95, f'--.-- uVrms', 
                          transform=ax.transAxes, fontsize=9,
                          bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                          ha='right', va='top')
            self.rms_texts.append(text)
    
    def load_data_from_txt(self, filepath):
        """从TXT文件加载OpenBCI数据"""
        try:
            print(f"正在读取: {os.path.basename(filepath)}")
            
            # 读取文件内容
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            data_lines = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('%') or line.startswith('#'):
                    continue
                
                # 尝试多种分隔符
                for sep in [',', '\t', ' ']:
                    if sep in line:
                        parts = [p.strip() for p in line.split(sep) if p.strip()]
                        if len(parts) >= 10:  # 至少有10列数据
                            try:
                                # 提取EEG通道数据（通常在第3-10列）
                                numeric_data = [float(p) for p in parts[2:10]]
                                data_lines.append(numeric_data)
                                break
                            except:
                                continue
            
            if not data_lines:
                print("未找到有效的EEG数据")
                return None
            
            data_array = np.array(data_lines)
            print(f"成功读取 {len(data_array)} 行EEG数据")
            return data_array
            
        except Exception as e:
            print(f"读取文件错误: {e}")
            return None
    
    def calculate_rms(self, data_buffer):
        """计算RMS值"""
        if len(data_buffer) == 0:
            return 0
        return np.sqrt(np.mean(np.array(data_buffer) ** 2))
    
    def update_animation(self, frame):
        """更新动画帧 - 实现从右向左滚动效果"""
        if not hasattr(self, 'eeg_data') or self.eeg_data is None:
            return self.lines + self.rms_texts
        
        if not hasattr(self, 'current_index'):
            self.current_index = 0
        
        # 每次更新添加新数据（模拟实时数据流）
        samples_to_add = min(5, len(self.eeg_data) - self.current_index)
        
        for _ in range(samples_to_add):
            if self.current_index < len(self.eeg_data):
                # 为每个通道添加新数据点（从右向左）
                for ch in range(8):
                    if ch < self.eeg_data.shape[1]:  # 确保不超出数据范围
                        self.data_buffers[ch].append(self.eeg_data[self.current_index, ch])
                    else:
                        self.data_buffers[ch].append(0)  # 用0填充缺失通道
                
                self.current_index += 1
        
        # 更新波形显示
        time_array = np.array(self.time_buffer)
        for ch in range(8):
            if ch < len(self.data_buffers):
                data_array = np.array(self.data_buffers[ch])
                self.lines[ch].set_data(time_array, data_array)
                
                # 自动调整Y轴范围
                if len(data_array) > 0:
                    y_range = max(50, np.max(np.abs(data_array)) * 1.2)
                    self.axes[ch].set_ylim(-y_range, y_range)
                
                # 更新RMS值
                rms_value = self.calculate_rms(self.data_buffers[ch])
                self.rms_texts[ch].set_text(f'{rms_value:5.2f} uVrms')
        
        return self.lines + self.rms_texts
    
    def start_display(self, filepath):
        """开始显示数据"""
        # 加载数据
        self.eeg_data = self.load_data_from_txt(filepath)
        
        if self.eeg_data is None:
            print("无法加载数据，使用模拟数据...")
            self.use_sample_data()
            return
        
        print(f"数据形状: {self.eeg_data.shape}")
        print("开始显示8通道波形（从右向左滚动）...")
        
        # 创建动画
        self.ani = animation.FuncAnimation(
            self.fig, self.update_animation, 
            interval=33,  # 约30fps
            blit=True, 
            cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()
    
    def use_sample_data(self):
        """使用模拟数据"""
        print("生成模拟EEG数据...")
        duration = 30  # 30秒
        n_samples = self.sample_rate * duration
        t = np.linspace(0, duration, n_samples)
        
        # 生成8通道模拟数据
        self.eeg_data = np.zeros((n_samples, 8))
        frequencies = [10, 20, 6, 15, 25, 8, 12, 18]
        
        for ch in range(8):
            # 基础脑电波 + 噪声
            base_signal = 20 * np.sin(2 * np.pi * frequencies[ch] * t)
            noise = np.random.normal(0, 3, n_samples)
            envelope = np.exp(-0.005 * t)
            self.eeg_data[:, ch] = base_signal * envelope + noise
        
        print("模拟数据生成完成")
        self.start_display(None)

def main():
    """主函数 - 使用示例"""
    # 文件路径（根据实际情况修改）
    filepath = r"openBCI_2013-12-24_meditation.txt"
    
    # 如果文件不存在，让用户选择
    if not os.path.exists(filepath):
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="选择OpenBCI数据文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        root.destroy()
    
    # 创建并启动显示器
    plotter = EEGWaveformPlotter(display_duration=10)
    
    if filepath and os.path.exists(filepath):
        plotter.start_display(filepath)
    else:
        print("使用模拟数据进行演示")
        plotter.use_sample_data()

if __name__ == "__main__":
    main()