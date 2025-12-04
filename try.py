import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import pandas as pd
import os
import time

class MultiChannelEEGPlotter:
    def __init__(self, sample_rate=250, display_duration=10):
        self.sample_rate = sample_rate
        self.display_duration = display_duration
        self.buffer_size = sample_rate * display_duration
        
        # 通道颜色配置
        self.channel_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
            '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
        ]
        
        self.setup_plot()
    
    def setup_plot(self):
        """设置8通道分开显示的图形界面"""
        self.fig, self.axes = plt.subplots(8, 1, figsize=(14, 10))
        plt.subplots_adjust(hspace=0.3)
        
        # 设置每个子图
        for i, ax in enumerate(self.axes):
            ax.set_facecolor('#f8f9fa')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(-self.display_duration, 0)
            ax.set_ylim(-100, 100)
            
            ax.set_ylabel(f'{i+1}', rotation=0, ha='right', va='center', 
                         fontsize=12, fontweight='bold', labelpad=20)
            
            if i < 7:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel('Time (s)', fontsize=12)
            
            # 颜色标识
            ax.text(-0.02, 0.5, '●', transform=ax.transAxes, 
                   fontsize=16, color=self.channel_colors[i],
                   ha='right', va='center')
        
        self.fig.suptitle('OpenBCI EEG Data - Multi Channel Display', 
                         fontsize=16, fontweight='bold', y=0.95)
        
        # 初始化数据缓冲区
        self.lines = []
        self.data_buffers = []
        self.time_buffer = deque([-self.display_duration + i/self.sample_rate 
                                 for i in range(self.buffer_size)], 
                                maxlen=self.buffer_size)
        
        for i, ax in enumerate(self.axes):
            line, = ax.plot([], [], color=self.channel_colors[i], linewidth=1.2)
            self.lines.append(line)
            buffer = deque([0] * self.buffer_size, maxlen=self.buffer_size)
            self.data_buffers.append(buffer)
        
        # RMS值显示
        self.rms_texts = []
        for i, ax in enumerate(self.axes):
            text = ax.text(0.98, 0.95, f'{i+1} --.-- uVrms', 
                          transform=ax.transAxes, fontsize=10,
                          bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                          ha='right', va='top')
            self.rms_texts.append(text)
        
        self.time_text = self.axes[-1].text(0.5, -0.2, '0 of 0 s', 
                                           transform=self.axes[-1].transAxes,
                                           fontsize=10, ha='center',
                                           bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
        
        self.real_time_text = self.axes[-1].text(0.85, -0.2, '', 
                                                transform=self.axes[-1].transAxes,
                                                fontsize=10, ha='center',
                                                bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
    
    def load_data_from_txt(self, filepath):
        """修复的数据读取函数 - 支持多种OpenBCI文件格式"""
        try:
            print(f"正在读取文件: {os.path.basename(filepath)}")
            
            # 方法1: 尝试pandas读取（更健壮）
            try:
                # 尝试读取CSV格式
                df = pd.read_csv(filepath, header=None, comment='%', engine='python')
                print(f"Pandas读取成功，形状: {df.shape}")
                
                # 查找包含数值数据的列
                numeric_columns = []
                for col in df.columns:
                    try:
                        # 检查列是否包含数值数据
                        sample_values = df[col].dropna().head(10)
                        if len(sample_values) > 0:
                            # 尝试转换为数值
                            pd.to_numeric(sample_values)
                            numeric_columns.append(col)
                    except:
                        continue
                
                if len(numeric_columns) >= 8:
                    # 提取前8个数值列作为EEG数据
                    eeg_data = df[numeric_columns[:8]].values
                    eeg_data = eeg_data[~np.isnan(eeg_data).any(axis=1)]  # 移除NaN行
                    
                    if len(eeg_data) > 0:
                        print(f"成功提取 {len(eeg_data)} 行EEG数据")
                        return eeg_data
                        
            except Exception as e:
                print(f"Pandas读取失败: {e}")
            
            # 方法2: 手动解析文件内容
            print("尝试手动解析文件...")
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            data_lines = []
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith('%') or line.startswith('#'):
                    continue
                
                # 更灵活的数据提取
                parts = []
                
                # 尝试多种分隔符
                for separator in [',', '\t', ' ']:
                    if separator in line:
                        parts = [part.strip() for part in line.split(separator) if part.strip()]
                        break
                
                if not parts:
                    continue
                
                # 提取所有可转换为数字的部分
                numeric_parts = []
                for part in parts:
                    try:
                        # 处理科学计数法和其他数字格式
                        value = float(part)
                        numeric_parts.append(value)
                    except ValueError:
                        # 如果不是数字，跳过
                        continue
                
                # 如果有足够的数据（至少4个通道）
                if len(numeric_parts) >= 4:
                    data_lines.append(numeric_parts)
            
            if not data_lines:
                print("未找到有效的数值数据")
                print("文件内容示例:")
                for i, line in enumerate(lines[:10]):  # 显示前10行
                    print(f"行{i+1}: {line}")
                return None
            
            # 转换为numpy数组
            data_array = np.array(data_lines)
            print(f"手动解析成功，找到 {len(data_array)} 行数据，{data_array.shape[1]} 列")
            
            # 如果列数多于8，取前8列
            if data_array.shape[1] > 8:
                data_array = data_array[:, :8]
                print(f"取前8列数据，最终形状: {data_array.shape}")
            
            return data_array
            
        except Exception as e:
            print(f"读取文件时发生错误: {e}")
            return None
    
    def calculate_rms(self, data_buffer):
        """计算RMS值"""
        if len(data_buffer) == 0:
            return 0
        return np.sqrt(np.mean(np.array(data_buffer) ** 2))
    
    def update_animation(self, frame):
        """更新动画帧"""
        if not hasattr(self, 'eeg_data') or self.eeg_data is None:
            return self.lines + self.rms_texts + [self.time_text, self.real_time_text]
        
        if not hasattr(self, 'current_index'):
            self.current_index = 0
        
        # 每次更新添加新数据
        samples_to_add = min(5, len(self.eeg_data) - self.current_index)
        
        for _ in range(samples_to_add):
            if self.current_index < len(self.eeg_data):
                # 为每个通道添加新数据点
                n_channels = min(8, self.eeg_data.shape[1])
                for ch in range(n_channels):
                    self.data_buffers[ch].append(self.eeg_data[self.current_index, ch])
                
                self.current_index += 1
        
        # 更新波形显示
        time_array = np.array(self.time_buffer)
        n_channels = min(8, self.eeg_data.shape[1])
        
        for ch in range(n_channels):
            data_array = np.array(self.data_buffers[ch])
            self.lines[ch].set_data(time_array, data_array)
            
            if len(data_array) > 0:
                y_range = max(50, np.max(np.abs(data_array)) * 1.2)
                self.axes[ch].set_ylim(-y_range, y_range)
            
            rms_value = self.calculate_rms(self.data_buffers[ch])
            self.rms_texts[ch].set_text(f'{ch+1} {rms_value:5.2f} uVrms')
        
        # 隐藏未使用的通道
        for ch in range(n_channels, 8):
            self.axes[ch].set_visible(False)
        
        # 更新时间显示
        if hasattr(self, 'eeg_data'):
            total_samples = len(self.eeg_data)
            current_time = self.current_index / self.sample_rate
            total_time = total_samples / self.sample_rate
            
            self.time_text.set_text(f'{current_time:.1f} of {total_time:.1f} s')
            self.real_time_text.set_text(time.strftime('%H:%M:%S'))
        
        return self.lines + self.rms_texts + [self.time_text, self.real_time_text]
    
    def start_display(self, filepath):
        """开始显示数据"""
        # 加载数据
        self.eeg_data = self.load_data_from_txt(filepath)
        
        if self.eeg_data is None:
            print("无法加载数据，尝试使用模拟数据...")
            self.use_sample_data()
            return
        
        print(f"数据形状: {self.eeg_data.shape}")
        print("开始显示波形...")
        
        # 创建动画
        self.ani = animation.FuncAnimation(
            self.fig, self.update_animation, 
            interval=33,
            blit=True, 
            cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()
    
    def use_sample_data(self):
        """使用模拟数据作为备选"""
        print("生成模拟EEG数据...")
        sample_rate = 250
        duration = 30
        n_samples = sample_rate * duration
        t = np.linspace(0, duration, n_samples)
        
        # 生成8通道模拟数据
        self.eeg_data = np.zeros((n_samples, 8))
        frequencies = [10, 20, 6, 15, 25, 8, 12, 18]
        
        for ch in range(8):
            # 基础脑电波
            base_signal = 20 * np.sin(2 * np.pi * frequencies[ch] * t)
            # 添加噪声
            noise = np.random.normal(0, 5, n_samples)
            # 添加衰减
            envelope = np.exp(-0.005 * t)
            self.eeg_data[:, ch] = base_signal * envelope + noise
        
        print("模拟数据生成完成，开始显示...")
        
        self.ani = animation.FuncAnimation(
            self.fig, self.update_animation, 
            interval=33,
            blit=True, 
            cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()

# 使用示例
def main():
    # 文件路径 - 使用更灵活的选择方式
    filepath = r"SDconverted-2016-12-17_18-28-40.txt"  # 你遇到问题的文件
    
    if not os.path.exists(filepath):
        # 在当前目录查找OpenBCI文件
        possible_files = [f for f in os.listdir('.') 
                         if f.endswith('.txt') and ('openBCI' in f or 'SDconverted' in f)]
        
        if possible_files:
            filepath = possible_files[0]
            print(f"自动选择文件: {filepath}")
        else:
            print("未找到数据文件，使用文件选择对话框...")
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename(
                title="选择OpenBCI数据文件",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            root.destroy()
    
    if not filepath or not os.path.exists(filepath):
        print("未选择有效文件，使用模拟数据演示")
        filepath = None
    
    # 创建并启动显示器
    plotter = MultiChannelEEGPlotter(display_duration=10)
    plotter.start_display(filepath)

if __name__ == "__main__":
    main()