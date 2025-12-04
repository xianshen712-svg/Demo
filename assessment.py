import tkinter as tk
from tkinter import messagebox

class ScaleAssessment:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(self.parent, text="量表评估", font=('Arial', 16)).pack(pady=10)
        
        scales = [
            'MMSE量表', 'HAMD量表', 'HAMA量表', 
            'MoCA量表', 'ADL量表', 'SDS量表'
        ]
        
        for scale in scales:
            btn = tk.Button(self.parent, text=scale, width=20, height=2,
                           command=lambda s=scale: self.open_scale(s))
            btn.pack(pady=5)
    
    def open_scale(self, scale_name):
        messagebox.showinfo("量表评估", f"打开{scale_name}")
        
if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    root.title('量表评估 测试')
    root.geometry('400x400')
    app = ScaleAssessment(root)
    root.mainloop()