import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from functools import partial
import sudokum
import concurrent.futures

# 例子使用：生成9个数独题目和答案
thread_count = 9

# 难度级别和对应的mask_rate
difficulty_mapping = {
    "新手": 0.1,
    "简单": 0.3,
    "中等": 0.5,
    "困难": 0.7,
    "地狱": 0.9,
}

# 默认难度级别
default_difficulty_level = "中等"

# 存储数独题目和答案
sudoku_puzzles = []
sudoku_answers = []

# 存储界面中的所有Entry
entries = []

# 当前选定的数独索引
current_thread = 0

# 创建游戏界面
def create_game_interface():
    global current_thread

    def main_interface():
        root = tk.Tk()
        root.geometry("400x300")
        root.title("数独启动")

        # 创建启动按钮
        def start_game():
            # 关闭主界面
            root.destroy()

            # 创建游戏界面
            create_game_interface()

        start_button = tk.Button(root, text="数独启动", command=start_game)
        start_button.pack(padx=20, pady=20)

        # 进入主事件循环
        root.mainloop()

    def generate_interface(thread_count):
        global notebook
        global entries
        global current_thread

        root = tk.Tk()
        root.title("原来，你也玩数独？")
        # root.geometry("600x800")

        # 创建数独和难度选择部分的Frame
        sudoku_frame = ttk.Frame(root)
        sudoku_frame.pack(side="left", padx=20, pady=20)

        # 创建难度选择部分
        difficulty_frame = ttk.Frame(sudoku_frame)
        difficulty_frame.pack(side="top", padx=10, pady=10)

        # 难度选择标签
        ttk.Label(difficulty_frame, text="难度选择").grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 难度选择按钮
        difficulty_buttons = {}
        for idx, difficulty in enumerate(["新手", "简单", "中等", "困难", "地狱"]):
            difficulty_buttons[difficulty] = tk.Button(difficulty_frame, text=difficulty, width=8,
                                                       command=partial(change_difficulty, difficulty, thread_count))
            difficulty_buttons[difficulty].grid(row=1 + idx // 3, column=idx % 3, padx=5, pady=5)

        # 创建Notebook
        notebook = ttk.Notebook(sudoku_frame)
        notebook.pack(side="top", padx=10, pady=10)

        # 在创建Entry小部件时根据数独题目的内容设置只读状态和可见性
        for i in range(thread_count):
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=f"Puzzle{i + 1}")

            # 为存储 Entry 对象的子列表初始化为空列表
            entry_row = []
            for row in range(9):
                entry_row.append([])
                for col in range(9):
                    cell_value = sudoku_puzzles[i][row][col]
                    entry = tk.Entry(frame, width=2, font=("Arial", 18))
                    entry.grid(row=row, column=col)
                    entry.bind('<Button-1>', lambda e, row=row, col=col: highlight_cell(row, col))
                    entry_row[row].append(entry)
                    
                    if cell_value != 0:
                        # 如果数独格子的值不为0，设置为只读状态并保持可见
                        entry.config(state='readonly', disabledbackground='white')
                        entry.delete(0, tk.END)
                        entry.insert(0, str(cell_value))
                    else:
                        # 如果数独格子的值为0，设置为可编辑状态
                        entry.config(state='normal')

            # 将 Entry 对象列表添加到 entries
            entries.append(entry_row)

        current_thread = 0  # 默认选中第一个数独

        # 更新数独显示
        switch_sudoku(None)

        # 绑定事件
        notebook.bind("<<NotebookTabChanged>>", switch_sudoku)

        # 创建数字选择部分的Frame
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

        # 更新非空白格子的背景色
        update_gray_cells(current_thread)

        # 添加数独规则按钮
        rule_button = tk.Button(root, text="数独规则", command=show_rule)
        rule_button.pack(padx=20, pady=20)

        root.mainloop()

    def generate_sudoku_puzzle(difficulty_level):
        # 获取对应难度级别的mask_rate
        mask_rate = difficulty_mapping.get(difficulty_level, 0.5)

        while True:
            # 使用sudokum生成数独题目
            puzzle = sudokum.generate(mask_rate)

            # 尝试解答数独题目
            solve_result = sudokum.solve(puzzle)

            if solve_result[0]:
                # 如果成功解答，返回数独的答案
                answer = solve_result[1]
                return puzzle, answer

    def generate_sudoku_parallel(thread_count, difficulty_level):
        # 定义线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 同时生成多个数独题目和答案
            results = [executor.submit(generate_sudoku_puzzle, difficulty_level) for _ in range(thread_count)]

            # 获取数独题目和答案
            sudoku_puzzles, sudoku_answers = zip(*[result.result() for result in results])

        return sudoku_puzzles, sudoku_answers

    def update_sudoku_display(idx):
        for i in range(9):
            for j in range(9):
                if sudoku_puzzles[idx][i][j] == 0:
                    entries[idx][i][j].delete(0, tk.END)
                    entries[idx][i][j].configure(bg='gray')
                else:
                    entries[idx][i][j].delete(0, tk.END)
                    entries[idx][i][j].insert(0, str(sudoku_puzzles[idx][i][j]))
                    entries[idx][i][j].configure(bg='white')

    def switch_sudoku(event):
        global notebook
        global current_thread
        idx = int(notebook.index(notebook.select()))
        current_thread = idx  # 更新 current_thread
        update_sudoku_display(idx)

    def highlight_cell(row, col):
        global current_thread

        # Reset previous highlight
        for i in range(9):
            for j in range(9):
                entries[current_thread][i][j].config(bg='white')

        # Set new highlight
        entries[current_thread][row][col].config(bg='yellow')

    def update_gray_cells(thread_idx):
        for row in range(9):
            for col in range(9):
                if sudoku_puzzles[thread_idx][row][col] != 0:
                    entries[thread_idx][row][col].config(bg='gray')
                    entries[thread_idx][row][col].configure(state='readonly')

    def init_white_cells(thread_idx):
        for row in range(9):
            for col in range(9):
                entries[thread_idx][row][col].config(bg='white')

    def show_rule():
        rule_window = tk.Toplevel()
        rule_window.title("数独规则")

        rule_text = """数独规则：
        1. 数字1-9在每行、每列和每个3x3宫格中只能出现一次。
        2. 数独谜题必须有唯一解。
        3. 数独谜题的初始数字越少，难度越大。
        """

        rule_label = tk.Label(rule_window, text=rule_text, justify="left")
        rule_label.pack(padx=20, pady=20)

    def change_difficulty(difficulty, thread_count):
        global current_difficulty
        global sudoku_puzzles
        global sudoku_answers

        current_difficulty = difficulty
        # 生成新的数独题目
        global current_thread
        current_thread = notebook.index(notebook.select())
        sudoku_puzzles, sudoku_answers = generate_sudoku_parallel(thread_count, difficulty)
        # 更新数独显示
        switch_sudoku(None)
        messagebox.showinfo("提示", f"已切换难度为 {difficulty}")
        # 更新非空白格子的背景色
        init_white_cells(current_thread)
        update_gray_cells(current_thread)

    def select_number(number):
        global current_thread

        for i in range(9):
            for j in range(9):
                if entries[current_thread][i][j].config('bg')[-1] == 'yellow':
                    entries[current_thread][i][j].delete(0, tk.END)
                    entries[current_thread][i][j].insert(0, str(number))

    def show_answer_grid(answer):
        answer_window = tk.Toplevel()
        answer_window.title("参考答案")

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

    # 启动游戏
    def start_game():
        global thread_count
        global sudoku_puzzles
        global sudoku_answers
        global entries
        global current_thread

        # 生成数独题目和答案
        while True:
            sudoku_puzzles, sudoku_answers = generate_sudoku_parallel(thread_count, default_difficulty_level)

            # 验证数独题目的唯一解性
            valid_puzzles = []
            for puzzle in sudoku_puzzles:
                solve_result = sudokum.solve(puzzle)
                if solve_result[0]:
                    valid_puzzles.append(puzzle)

            if len(valid_puzzles) == thread_count:
                # 所有数独题目都有唯一解
                break

        # 生成界面
        generate_interface(thread_count)

    # 创建启动按钮
    root = tk.Tk()
    root.geometry("300x80")
    root.title("数独启动")
    start_button = tk.Button(root, text="数独启动", command=start_game)
    start_button.pack(padx=20, pady=20)
    root.mainloop()

if __name__ == "__main__":
    create_game_interface()
