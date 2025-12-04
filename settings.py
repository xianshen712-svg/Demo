import tkinter as tk
from tkinter import messagebox

class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("系统设置")
        self.parent.geometry("400x300")
        self.setup_ui()
    
    def setup_ui(self):
        # 基本设置
        basic_frame = tk.LabelFrame(self.parent, text="基本设置", font=('Arial', 10))
        basic_frame.pack(fill='x', padx=10, pady=5)
        
        settings = [
            ('自动保存', tk.BooleanVar(value=True)),
            ('声音提示', tk.BooleanVar(value=True)),
            ('自动更新', tk.BooleanVar(value=False))
        ]
        
        for text, var in settings:
            cb = tk.Checkbutton(basic_frame, text=text, variable=var)
            cb.pack(anchor='w', padx=10, pady=2)
        
        # 保存按钮
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="保存设置", command=self.save_settings).pack(side='left', padx=10)
        tk.Button(btn_frame, text="取消", command=self.parent.destroy).pack(side='left', padx=10)
    
    def save_settings(self):
        messagebox.showinfo("设置", "设置已保存")
        self.parent.destroy()
        
# ...existing code...
if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    SettingsWindow(root)
    root.mainloop()