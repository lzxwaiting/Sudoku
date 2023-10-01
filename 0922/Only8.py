import random
import copy
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from functools import partial
import os

N = 9


def is_valid_move(board, row, col, num):
    # 检查行、列和3x3宫格是否有重复
    for i in range(N):
        if board[row][i] == num or board[i][col] == num:
            return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == num:
                return False

    return True

def solve_sudoku(board):
    def backtrack(row, col):
        if row == N:
            return True

        next_row = row + 1 if col == N - 1 else row
        next_col = col + 1 if col < N - 1 else 0

        if board[row][col] != 0:
            return backtrack(next_row, next_col)

        for num in range(1, N + 1):
            if is_valid_move(board, row, col, num):
                board[row][col] = num
                if backtrack(next_row, next_col):
                    return True
                board[row][col] = 0

        return False

    return backtrack(0, 0)

def generate_sudoku(difficulty, filename=None):
    board = [[0] * N for _ in range(N)]

    # 生成一个有解的数独
    solve_sudoku(board)

    # 根据难度级别清除数字
    if difficulty == 'easy':
        num_to_remove = 30
    elif difficulty == 'medium':
        num_to_remove = 40
    elif difficulty == 'hard':
        num_to_remove = 50
    else:
        raise ValueError('Invalid difficulty level')

    while num_to_remove > 0:
        row, col = random.randint(0, N - 1), random.randint(0, N - 1)
        if board[row][col] != 0:
            # 先备份当前的值
            backup = board[row][col]
            board[row][col] = 0

            # 检查是否有唯一解
            temp_board = copy.deepcopy(board)
            num_solutions = count_solutions(temp_board)
            if num_solutions != 1:
                # 如果有多个解，则恢复备份的值
                board[row][col] = backup
            else:
                num_to_remove -= 1

    # 如果指定了文件名，则将数独保存到文件中
    if filename is not None:
        with open(filename, 'w') as f:
            for row in board:
                f.write(' '.join(map(str, row)) + '\n')

    return board

def load_sudoku(filename):
    filepath = os.path.join(os.getcwd(), filename)
    board = []
    with open(filepath, 'r') as f:
        for line in f:
            row = list(map(int, line.strip().split()))
            board.append(row)
    return board


def count_solutions(board):
    # 计算数独的解的数量
    def backtrack(row, col):
        if row == N:
            return 1

        next_row = row + 1 if col == N - 1 else row
        next_col = col + 1 if col < N - 1 else 0

        if board[row][col] != 0:
            return backtrack(next_row, next_col)

        count = 0
        for num in range(1, N + 1):
            if is_valid_move(board, row, col, num):
                board[row][col] = num
                count += backtrack(next_row, next_col)
                board[row][col] = 0

        return count

    return backtrack(0, 0)

class SudokuGUI:
    def __init__(self, master, sudoku_list):
        self.master = master
        self.sudoku_list = sudoku_list
        self.current_selected_cell = None
        self.current_thread = 0  # Default to the first thread
        self.entries = []
        self.sudoku_answers = None
        self.current_difficulty = "中等"
        self.sudoku_count = len(sudoku_list)

        self.generate_interface()

    # 更新数独显示
    def update_sudoku_display(self, idx):
        for i in range(9):
            for j in range(9):
                if self.sudoku_list[idx][i][j] == 0:
                    self.entries[idx][i][j].delete(0, tk.END)
                else:
                    self.entries[idx][i][j].delete(0, tk.END)
                    self.entries[idx][i][j].insert(0, str(self.sudoku_list[idx][i][j]))

    # 切换数独题目
    def switch_sudoku(self, event):
        idx = int(self.notebook.index(self.notebook.select()))
        self.update_sudoku_display(idx)

    # 函数：高亮格子并绑定数字选择事件
    def highlight_cell(self, row, col):
        # Reset previous highlight
        if self.current_selected_cell:
            self.entries[self.current_selected_cell[0]][self.current_selected_cell[1]][self.current_selected_cell[2]].config(bg='white')

        # Set new highlight
        self.entries[self.current_thread][row][col].config(bg='yellow')
        self.current_selected_cell = (self.current_thread, row, col)

    # 用于更新非空白格子的背景色
    def update_gray_cells(self, thread_idx):
        for row in range(9):
            for col in range(9):
                if self.sudoku_list[thread_idx][row][col] != 0:
                    self.entries[thread_idx][row][col].config(bg='gray')

    def init_white_cells(self, thread_idx):
        for row in range(9):
            for col in range(9):
                self.entries[thread_idx][row][col].config(bg='white')

    # 生成界面
    def generate_interface(self):
        self.master.title("数独")

        # 创建标签页
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack()

        for i in range(self.sudoku_count):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f"题目{i + 1}")

            # 为存储 Entry 对象的子列表初始化为空列表
            entry_row = []
            for row in range(9):
                entry_row.append([])
                for col in range(9):
                    entry = tk.Entry(frame, width=2, font=("Arial", 18))
                    entry.grid(row=row, column=col)
                    entry.bind('<Button-1>', lambda e, row=row, col=col: self.highlight_cell(row, col))
                    entry_row[row].append(entry)

            # 将 Entry 对象列表添加到 entries
            self.entries.append(entry_row)

        self.current_selected_cell = None
        self.current_thread = 0  # Default to the first thread

        # 更新数独显示
        self.switch_sudoku(None)

        # 绑定事件
        self.notebook.bind("<<NotebookTabChanged>>", self.switch_sudoku)

        # 创建难度选择部分
        difficulty_frame = ttk.Frame(self.master)
        difficulty_frame.pack(side="right", padx=20, pady=20)

        # 难度选择标签
        ttk.Label(difficulty_frame, text="难度选择").grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 难度选择按钮
        difficulty_buttons = {}
        for idx, difficulty in enumerate(["新手", "简单", "中等", "困难", "地狱"]):
            difficulty_buttons[difficulty] = tk.Button(difficulty_frame, text=difficulty, width=8,
                                                       command=partial(self.change_difficulty, difficulty, self.sudoku_count))
            difficulty_buttons[difficulty].grid(row=1 + idx // 3, column=idx % 3, padx=5, pady=5)

        # 数字选择部分
        number_frame = ttk.Frame(self.master)
        number_frame.pack(side="right", padx=20, pady=20)

        ttk.Label(number_frame, text="数字选择").grid(row=0, column=0, columnspan=3, pady=(0, 10))

        for i in range(3):
            for j in range(3):
                button_number = i * 3 + j + 1
                button = tk.Button(number_frame, text=str(button_number), width=8, command=partial(self.select_number, button_number))
                button.grid(row=i + 1, column=j, padx=5, pady=5)

        # 添加显示答案按钮
        show_answer_button = tk.Button(number_frame, text="显示答案", width=8, command=self.show_answer)
        show_answer_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        self.update_gray_cells(self.current_thread)

    # 函数：切换难度
    def change_difficulty(self, difficulty, sudoku_count):
        self.current_difficulty = difficulty
        # 生成新的数独题目
        self.sudoku_list = generate_sudoku_parallel(sudoku_count, difficulty)
        # 更新数独显示
        self.switch_sudoku(None)
        messagebox.showinfo("提示", f"已切换难度为 {difficulty}")
        # 更新非空白格子的背景色
        self.init_white_cells(self.current_thread)
        self.update_gray_cells(self.current_thread)

    # 函数：选择数字
    def select_number(self, number):
        if self.current_selected_cell:
            self.entries[self.current_selected_cell[0]][self.current_selected_cell[1]][self.current_selected_cell[2]].delete(0, tk.END)
            self.entries[self.current_selected_cell[0]][self.current_selected_cell[1]][self.current_selected_cell[2]].insert(0, str(number))
            self.current_selected_cell = None

    # 显示答案
    def show_answer_grid(self, answer):
        answer_window = tk.Toplevel()
        answer_window.title("答案")

        for i in range(9):
            for j in range(9):
                entry = tk.Entry(answer_window, width=2, font=("Arial", 18), justify="center", bd=2, relief="solid")
                entry.grid(row=i, column=j)
                entry.insert(0, str(answer[i][j]))
                entry.configure(state='readonly')

    def show_answer(self):
        # 获取当前选定的数独索引
        idx = int(self.notebook.index(self.notebook.select()))

        # 确保该数独索引有答案
        if self.sudoku_answers and len(self.sudoku_answers) > idx:
            answer = self.sudoku_answers[idx]
            self.show_answer_grid(answer)
# 打印数独题目
def print_sudoku(board):
    for row in board:
        print(row)

def save_sudoku_problem(board, filename):
    with open(filename, 'w') as file:
        for row in board:
            file.write(' '.join(map(str, row)) + '\n')

def save_sudoku_solution(board, filename):
    with open(filename, 'w') as file:
        for row in board:
            file.write(' '.join(map(str, row)) + '\n')

def generate_sudoku_parallel():
    sudoku_list = []
    threads = []

    def generate_and_append_sudoku():
        sudoku = generate_sudoku()
        sudoku_list.append(sudoku)

    # 创建9个线程，每个线程生成一个数独
    for _ in range(9):
        thread = threading.Thread(target=generate_and_append_sudoku)
        threads.append(thread)

    # 启动线程并等待完成
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return sudoku_list
def load_sudoku_list(filename):
    sudoku_list = []

    with open(filename, "r") as file:
        for line in file:
            # 将每一行转换为列表
            row = list(map(int, line.strip().split()))

            # 将列表添加到数独列表中
            sudoku_list.append(row)

    return sudoku_list

#在main函数中调用GUI
if __name__ == "__main__":
    root = tk.Tk()
    sudoku_list = generate_sudoku_parallel()
    # sudoku_list = load_sudoku_list("sudoku_list.txt")
    sudoku_gui = SudokuGUI(root,sudoku_list)
    root.mainloop()