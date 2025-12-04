import tkinter as tk
from tkinter import ttk, messagebox

class PatientManager:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        # 患者列表
        list_frame = tk.Frame(self.parent)
        list_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(list_frame, text="患者列表", font=('Arial', 14)).pack(anchor='w')
        
        # 搜索框
        search_frame = tk.Frame(list_frame)
        search_frame.pack(fill='x', pady=5)
        tk.Entry(search_frame).pack(side='left', fill='x', expand=True)
        tk.Button(search_frame, text="搜索").pack(side='right', padx=5)
        
        # 患者表格
        columns = ('姓名', '年龄', '病历号', '最后检测')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 示例数据
        patients = [
            ('张三', '35', '20240001', '2024-01-20'),
            ('李四', '28', '20240002', '2024-01-19'),
            ('王五', '45', '20240003', '2024-01-18')
        ]
        
        for patient in patients:
            self.tree.insert('', 'end', values=patient)
        
        self.tree.pack(fill='both', expand=True)
        
        # 操作按钮
        btn_frame = tk.Frame(list_frame)
        btn_frame.pack(fill='x', pady=5)
        tk.Button(btn_frame, text="新增患者", command=self.add_patient).pack(side='left', padx=2)
        tk.Button(btn_frame, text="编辑", command=self.edit_patient).pack(side='left', padx=2)
        tk.Button(btn_frame, text="删除", command=self.delete_patient).pack(side='left', padx=2)
    
    def add_patient(self):
        messagebox.showinfo("患者管理", "新增患者")
    
    def edit_patient(self):
        messagebox.showinfo("患者管理", "编辑患者信息")
    
    def delete_patient(self):
        messagebox.showinfo("患者管理", "删除患者")
        
# ...existing code...
if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    root.title('患者管理 测试')
    root.geometry('600x400')
    app = PatientManager(root)
    root.mainloop()