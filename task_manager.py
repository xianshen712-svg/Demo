import tkinter as tk
from tkinter import messagebox

class TaskManager:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(self.parent, text="任务管理", font=('Arial', 16)).pack(pady=10)
        
        # 任务列表
        tasks = ['静息态记录', '任务态记录', '事件相关电位', '睡眠监测']
        
        for task in tasks:
            frame = tk.Frame(self.parent)
            frame.pack(fill='x', padx=20, pady=5)
            tk.Label(frame, text=task, width=15, anchor='w').pack(side='left')
            tk.Button(frame, text="开始", command=lambda t=task: self.start_task(t)).pack(side='right')
    
    def start_task(self, task_name):
        messagebox.showinfo("任务管理", f"开始任务: {task_name}")
        
if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    root.title('任务管理 测试')
    root.geometry('400x300')
    app = TaskManager(root)
    root.mainloop()