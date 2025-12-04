import tkinter as tk
from tkinter import Scale, messagebox

class FlashControl:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(self.parent, text="频闪避控设置", font=('Arial', 16)).pack(pady=10)
        
        # 频率控制
        freq_frame = tk.Frame(self.parent)
        freq_frame.pack(pady=10)
        tk.Label(freq_frame, text="频率 (Hz):").pack()
        self.freq_scale = Scale(freq_frame, from_=1, to=30, orient='horizontal')
        self.freq_scale.set(10)
        self.freq_scale.pack()
        
        # 强度控制
        intensity_frame = tk.Frame(self.parent)
        intensity_frame.pack(pady=10)
        tk.Label(intensity_frame, text="强度:").pack()
        self.intensity_scale = Scale(intensity_frame, from_=0, to=100, orient='horizontal')
        self.intensity_scale.set(50)
        self.intensity_scale.pack()
        
        # 控制按钮
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="开始频闪", command=self.start_flash).pack(side='left', padx=10)
        tk.Button(btn_frame, text="停止", command=self.stop_flash).pack(side='left', padx=10)
    
    def start_flash(self):
        freq = self.freq_scale.get()
        intensity = self.intensity_scale.get()
        messagebox.showinfo("频闪避控", f"开始频闪: {freq}Hz, 强度: {intensity}%")
    
    def stop_flash(self):
        messagebox.showinfo("频闪避控", "停止频闪")
        
# ...existing code...
if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    root.title('频闪避控 测试')
    root.geometry('480x360')
    app = FlashControl(root)
    root.mainloop()