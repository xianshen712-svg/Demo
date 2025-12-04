import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
from datetime import datetime

class EventMarker:
    def __init__(self, parent):
        self.parent = parent
        self.events = []  
        self.setup_ui()
    
    def setup_ui(self):
        # 主容器
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建选项卡
        self.create_tabs(main_frame)
    
    def create_tabs(self, parent):
        """创建选项卡控件"""
        tab_control = ttk.Notebook(parent)
        
        # 事件标记标签页
        event_marker_tab = ttk.Frame(tab_control)
        tab_control.add(event_marker_tab, text='事件标记')
        
        # 事件列表标签页
        event_list_tab = ttk.Frame(tab_control)
        tab_control.add(event_list_tab, text='事件列表')
        
        tab_control.pack(fill='both', expand=True)
        
        # 设置标签页内容
        self.setup_event_marker_tab(event_marker_tab)
        self.setup_event_list_tab(event_list_tab)
    
    def setup_event_marker_tab(self, parent):
        """设置事件标记标签页 - 根据图片精确实现"""
        # 事件组合选择区域
        combo_frame = tk.Frame(parent, bg='white')
        combo_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(combo_frame, text="默认事件组合", bg='white',
                font=('Arial', 10)).pack(side='left')
        
        self.event_combo_var = tk.StringVar(value="标准事件组")
        event_combos = ttk.Combobox(combo_frame, textvariable=self.event_combo_var,
                                values=["标准事件组", "睡眠监测组", "认知测试组", "癫痫监测组"],
                                state="readonly", width=10)
        event_combos.pack(side='left', padx=5)
        event_combos.bind('<<ComboboxSelected>>', self.on_combo_change)
        
        # 新建组合按钮
        new_combo_btn = tk.Button(combo_frame, text="新建组合", 
                                command=self.create_new_combo,
                                font=('Arial', 9), bg='#4ECDC4', fg='white')
        new_combo_btn.pack(side='left', padx=10)
        
        # 事件按钮区域 - 垂直排列
        self.create_vertical_event_buttons(parent)

    def create_vertical_event_buttons(self, parent):
        """创建垂直排列的事件按钮 - 根据图片精确实现"""
        # 创建滚动框架
        canvas = tk.Canvas(parent, bg='white', height=350)  # 调整高度
        scrollbar = tk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 根据图片中的事件分类和顺序
        event_categories = [
            ('基础事件', ['睁眼', '闭眼', '深呼吸', '过度换气']),
            ('认知事件', ['心算'])  # 图片中只显示了心算
        ]
        
        row = 0
        for category, events in event_categories:
            # 分类标题
            category_label = tk.Label(scrollable_frame, text=category, 
                                    font=('Arial', 11, 'bold'), bg='white',
                                    anchor='w')
            category_label.grid(row=row, column=0, columnspan=2, 
                            sticky='w', padx=5, pady=(15, 5))
            row += 1
            
            # 创建事件按钮
            for event in events:
                # 事件行容器
                event_row = tk.Frame(scrollable_frame, bg='white')
                event_row.grid(row=row, column=0, columnspan=2, 
                            sticky='ew', padx=5, pady=2)
                
                # 事件标签 - 左对齐
                event_label = tk.Label(event_row, text=event, bg='white',
                                    font=('Arial', 10), width=12, anchor='w')
                event_label.pack(side='left', padx=(0, 10))
                
                # 标记按钮 - 红色，右对齐
                mark_btn = tk.Button(event_row, text="标记", 
                                command=lambda e=event: self.mark_event(e),
                                font=('Arial', 9), bg='#FF4444', fg='white',
                                width=6, height=1)
                mark_btn.pack(side='right')
                
                row += 1
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_event_list_tab(self, parent):
        """设置事件列表标签页"""
        # 搜索和过滤区域
        search_frame = tk.Frame(parent, bg='white')
        search_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame, text="搜索:", bg='white',
                font=('Arial', 9)).pack(side='left')
        
        search_entry = tk.Entry(search_frame, width=20, font=('Arial', 9))
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.search_events)
        
        # 事件列表表格
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建表格
        columns = ('时间', '事件类型', '持续时间', '备注')
        self.event_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题
        for col in columns:
            self.event_tree.heading(col, text=col)
            self.event_tree.column(col, width=100)
        
        # 添加示例数据
        self.add_sample_events()
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.event_tree.yview)
        self.event_tree.configure(yscrollcommand=scrollbar.set)
        
        self.event_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 操作按钮区域
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        buttons = [
            ('清空列表', self.clear_event_list, '#FF9F43'),
            ('导出数据', self.export_events, '#10AC84'),
            ('删除选中', self.delete_selected, '#FF6B6B'),
            ('添加备注', self.add_note, '#54A0FF')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                          font=('Arial', 9), bg=color, fg='white', width=10)
            btn.pack(side='left', padx=5)
    
    def on_combo_change(self, event):
        """事件组合改变"""
        selected_combo = self.event_combo_var.get()
        messagebox.showinfo("组合切换", f"切换到事件组合: {selected_combo}")
    
    def mark_event(self, event_type):
        """标记事件"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # 创建新事件
        new_event = {
            'time': current_time,
            'type': event_type,
            'duration': '0秒',
            'note': '自动标记'
        }
        self.events.append(new_event)
        
        # 添加到事件列表
        self.event_tree.insert('', 'end', values=(
            new_event['time'],
            new_event['type'],
            new_event['duration'],
            new_event['note']
        ))
        
        # 显示成功消息
        messagebox.showinfo("事件标记", f"成功标记事件: {event_type}\n时间: {current_time}")
    
    def add_sample_events(self):
        """添加示例事件数据"""
        sample_events = [
            ('10:23:15', '睁眼', '5秒', '基线记录'),
            ('10:23:45', '闭眼', '30秒', '静息状态'),
            ('10:24:20', '深呼吸', '15秒', '诱发测试'),
            ('10:25:10', '心算', '45秒', '认知任务'),
            ('10:26:05', '光刺激', '10秒', '视觉诱发')
        ]
        
        for event in sample_events:
            self.event_tree.insert('', 'end', values=event)
            self.events.append({
                'time': event[0],
                'type': event[1],
                'duration': event[2],
                'note': event[3]
            })
    
    def search_events(self, event):
        """搜索事件"""
        search_term = event.widget.get().lower()
        
        # 清空当前显示
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
        
        # 重新添加匹配的事件
        for event_data in self.events:
            if (search_term in event_data['type'].lower() or 
                search_term in event_data['note'].lower() or
                search_term in event_data['time']):
                self.event_tree.insert('', 'end', values=(
                    event_data['time'],
                    event_data['type'],
                    event_data['duration'],
                    event_data['note']
                ))
    
    def clear_event_list(self):
        """清空事件列表"""
        if messagebox.askyesno("确认清空", "确定要清空所有事件记录吗？"):
            for item in self.event_tree.get_children():
                self.event_tree.delete(item)
            self.events.clear()
            messagebox.showinfo("清空", "事件列表已清空")
    
    def export_events(self):
        """导出事件数据"""
        if not self.events:
            messagebox.showwarning("导出", "没有事件数据可导出")
            return
        
        # 模拟导出过程
        filename = f"事件记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        messagebox.showinfo("导出成功", f"事件数据已导出到: {filename}")
    
    def delete_selected(self):
        """删除选中事件"""
        selected_items = self.event_tree.selection()
        if not selected_items:
            messagebox.showwarning("删除", "请先选择要删除的事件")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_items)} 个事件吗？"):
            for item in selected_items:
                # 从事件列表中删除
                item_values = self.event_tree.item(item)['values']
                for i, event_data in enumerate(self.events):
                    if (event_data['time'] == item_values[0] and 
                        event_data['type'] == item_values[1]):
                        del self.events[i]
                        break
                
                # 从树形视图中删除
                self.event_tree.delete(item)
    
    def add_note(self):
        """为选中事件添加备注"""
        selected_items = self.event_tree.selection()
        if not selected_items:
            messagebox.showwarning("备注", "请先选择要添加备注的事件")
            return
        
        if len(selected_items) > 1:
            messagebox.showwarning("备注", "一次只能为一个事件添加备注")
            return
        
        item = selected_items[0]
        current_note = self.event_tree.item(item)['values'][3]
        
        # 弹出备注输入对话框
        note = simpledialog.askstring("添加备注", "请输入备注:", 
                                       initialvalue=current_note)
        if note is not None:
            # 更新树形视图
            values = list(self.event_tree.item(item)['values'])
            values[3] = note
            self.event_tree.item(item, values=values)
            
            # 更新事件列表
            for event_data in self.events:
                if (event_data['time'] == values[0] and 
                    event_data['type'] == values[1]):
                    event_data['note'] = note
                    break
    
    def create_new_combo(self):
        """新建事件组合"""
        # 弹出新建组合对话框
        combo_name = simpledialog.askstring("新建组合", "请输入新组合名称:")
        if combo_name:
            messagebox.showinfo("新建组合", f"成功创建事件组合: {combo_name}")
            # 这里可以添加实际的组合创建逻辑
            
# ...existing code...
if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    root.title('事件标记 测试')
    root.geometry('420x640')
    app = EventMarker(root)
    root.mainloop()