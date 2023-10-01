import tkinter as tk
# import ttkbootstrap as ttk
# from ttkbootstrap.constants import *
from tkinter import messagebox
from functools import partial
from tkinter import ttk

import sudokum
import concurrent.futures

difficulty_mapping = {
    "新手":0.1,
    "简单":0.3,
    "中等":0.5,
    "困难":0.7,
    "地狱":0.9,
}

default_difficulty_level="中等"

#根据难度生成数独题目
def generate_sudoku_puzzle(difficulty_level):
    # 获取对应难度级别的mask_rate
    mask_rate = difficulty_mapping.get(difficulty_level, 0.5)
    
    while True:
        # 获取对应难度级别的mask_rate
        mask_rate = difficulty_mapping.get(difficulty_level, 0.5)

        # 使用sudokum生成数独题目
        puzzle = sudokum.generate(mask_rate)

        # 尝试解答数独题目
        solve_result = sudokum.solve(puzzle)
    
        if solve_result[0]:
            # 如果成功解答，返回数独的答案
            answer = solve_result[1]
            return puzzle , answer

#根据线程数生成多个数独
def generate_sudoku_parallel(thread_count, difficulty_level):
    # 定义线程池
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        # 同时生成多个数独题目和答案
        results = [executor.submit(generate_sudoku_puzzle, difficulty_level) for _ in range(thread_count)]
        
        # 获取数独题目和答案
        sudoku_puzzles, sudoku_answers = zip(*[result.result() for result in results])
    
    return sudoku_puzzles, sudoku_answers

thread_count = 9
sudoku_puzzles, sudoku_answers = generate_sudoku_parallel(thread_count, "地狱")

# 更新数独显示
def update_sudoku_display(idx):
    for i in range(9):
        for j in range(9):
            if sudoku_puzzles[idx][i][j] == 0:
                entries[idx][i][j].delete(0, tk.END)
            else:
                entries[idx][i][j].delete(0, tk.END)
                entries[idx][i][j].insert(0, str(sudoku_puzzles[idx][i][j]))

# 切换数独题目
def switch_sudoku(event):
    global notebook
    idx = int(notebook.index(notebook.select()))
    update_sudoku_display(idx)

# 函数：高亮格子并绑定数字选择事件
def highlight_cell(row, col):
    global current_selected_cell

    # Reset previous highlight
    if current_selected_cell:
        entries[current_selected_cell[0]][current_selected_cell[1]][current_selected_cell[2]].config(bg='white')

    # Set new highlight
    entries[current_thread][row][col].config(bg='yellow')
    current_selected_cell = (current_thread, row, col)

# 用于更新非空白格子的背景色
def update_gray_cells(thread_idx):
    for row in range(9):
        for col in range(9):
            if sudoku_puzzles[thread_idx][row][col] != 0:
                entries[thread_idx][row][col].config(bg='gray')

def init_white_cells(thread_idx):
    for row in range(9):
        for col in range(9):
            entries[thread_idx][row][col].config(bg='white')

# 生成界面
def generate_interface(thread_count):
    global notebook
    global entries
    global current_thread
    global current_selected_cell

    root = tk.Tk()
    root.title("数多窟")

    # 创建标签页
    notebook = ttk.Notebook(root)
    notebook.pack()

    for i in range(thread_count):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=f"Puzzle{i + 1}")

        # 为存储 Entry 对象的子列表初始化为空列表
        entry_row = []
        for row in range(9):
            entry_row.append([])
            for col in range(9):
                entry = tk.Entry(frame, width=2, font=("Arial", 18))
                entry.grid(row=row, column=col)
                entry.bind('<Button-1>', lambda e, row=row, col=col: highlight_cell(row, col))
                entry_row[row].append(entry)

        # 将 Entry 对象列表添加到 entries
        entries.append(entry_row)

    current_selected_cell = None
    current_thread = 0  # Default to the first thread

    # 更新数独显示
    switch_sudoku(None)

    # 绑定事件
    notebook.bind("<<NotebookTabChanged>>", switch_sudoku)

    # 创建难度选择部分
    difficulty_frame = ttk.Frame(root)
    difficulty_frame.pack(side="right", padx=20, pady=20)

    # 难度选择标签
    ttk.Label(difficulty_frame, text="难度选择").grid(row=0, column=0, columnspan=3, pady=(0, 10))

    # 难度选择按钮
    difficulty_buttons = {}
    for idx, difficulty in enumerate(["新手", "简单", "中等", "困难", "地狱"]):
        difficulty_buttons[difficulty] = tk.Button(difficulty_frame, text=difficulty, width=8,
                                                   command=partial(change_difficulty, difficulty, thread_count))
        difficulty_buttons[difficulty].grid(row=1 + idx // 3, column=idx % 3, padx=5, pady=5)

    # 数字选择部分
    number_frame = ttk.Frame(root)
    number_frame.pack(side="right", padx=20, pady=20)

    ttk.Label(number_frame, text="数字选择").grid(row=0, column=0, columnspan=3, pady=(0, 10))

    for i in range(3):
        for j in range(3):
            button_number = i * 3 + j + 1
            button = tk.Button(number_frame, text=str(button_number), width=8, command=partial(select_number, button_number))
            button.grid(row=i + 1, column=j, padx=5, pady=5)

    # 添加显示答案按钮
    show_answer_button = tk.Button(number_frame, text="显示答案", width=8, command=show_answer)
    show_answer_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

    update_gray_cells(current_thread)
    root.mainloop()

# 函数：切换难度
def change_difficulty(difficulty, thread_count):
    global current_difficulty
    global sudoku_puzzles
    global sudoku_answers

    current_difficulty = difficulty
    # 生成新的数独题目
    global current_thread
    current_thread = notebook.index(notebook.select())
    sudoku_puzzles , sudoku_answers = generate_sudoku_parallel(thread_count, difficulty)
    # 更新数独显示
    switch_sudoku(None)
    messagebox.showinfo("提示", f"已切换难度为 {difficulty}")
    # 更新非空白格子的背景色
    init_white_cells(current_thread)
    update_gray_cells(current_thread)

# 函数：选择数字
def select_number(number):
    global current_thread
    global current_selected_cell

    if current_selected_cell:
        entries[current_selected_cell[0]][current_selected_cell[1]][current_selected_cell[2]].delete(0, tk.END)
        entries[current_selected_cell[0]][current_selected_cell[1]][current_selected_cell[2]].insert(0, str(number))
        current_selected_cell = None

#显示答案
def show_answer_grid(answer):
    answer_window = tk.Toplevel()
    answer_window.title("答案")

    for i in range(9):
        for j in range(9):
            entry = tk.Entry(answer_window, width=2, font=("Arial", 18), justify="center", bd=2, relief="solid")
            entry.grid(row=i, column=j)
            entry.insert(0, str(answer[i][j]))
            entry.configure(state='readonly')  

def show_answer():
    global current_thread

    # 获取当前选定的数独索引
    idx = int(notebook.index(notebook.select()))

    # 确保该数独索引有答案
    if sudoku_answers and len(sudoku_answers) > idx:
        answer = sudoku_answers[idx]
        show_answer_grid(answer)

# 例子使用：生成9个数独题目和答案
thread_count = 9
sudoku_puzzles , sudoku_answers = generate_sudoku_parallel(thread_count, "中等")

# 存储界面中的所有Entry
entries = []

# 生成界面
generate_interface(thread_count)