import random
import copy
import threading
import tkinter as tk
from tkinter import ttk

# class SudokuGUI:
#     def __init__(self, master):
#         self.master = master
#         self.master.title("Sudoku")
#         self.master.geometry("600x400")

#         # 创建 Notebook 控件
#         self.notebook = ttk.Notebook(self.master)
#         self.notebook.pack(fill=tk.BOTH, expand=True)

#         # 创建第一页
#         self.page1 = ttk.Frame(self.notebook)
#         self.notebook.add(self.page1, text="开始")

#         # 创建第二页
#         self.page2 = ttk.Frame(self.notebook)
#         self.notebook.add(self.page2, text="选择题目")

#         # 添加 9 个选项卡
#         for i in range(1, 10):
#             puzzle_board, solved_board = generate_sudoku()
#             tab = ttk.Frame(self.page2)
#             self.notebook.add(tab, text=f"题目{i}")
#             puzzle_label = tk.Label(tab, text="题目:")
#             puzzle_label.pack()
#             puzzle_text = tk.Text(tab, height=10, width=20)
#             puzzle_text.insert(tk.END, "\n".join(" ".join(str(num) for num in row) for row in puzzle_board))
#             puzzle_text.pack()
#             solution_button = tk.Button(tab, text="查看答案", command=lambda board=solved_board: self.show_solution(board))
#             solution_button.pack()

#         # 添加开始游戏的按钮
#         start_button = tk.Button(self.page1, text="开始游戏", command=self.start_game)
#         start_button.pack()

#     def start_game(self):
#         self.notebook.select(self.page2)

#     def show_solution(self, board):
#         solution_window = tk.Toplevel(self.master)
#         solution_window.title("题解")
#         solution_text = tk.Text(solution_window, height=10, width=20)
#         solution_text.insert(tk.END, "\n".join(" ".join(str(num) for num in row) for row in board))
#         solution_text.pack()

N = 9
# 调用 generate_sudoku 函数并传入难度级别（清除的数字数量）


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

def generate_sudoku(difficulty):
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
    def __init__(self, master):
        self.master = master
        self.master.title("Sudoku")
        self.master.geometry("600x400")

        # 创建 Notebook 控件
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建第一页
        self.page1 = ttk.Frame(self.notebook)
        self.notebook.add(self.page1, text="开始")

        # 创建第二页
        self.page2 = ttk.Frame(self.notebook)
        self.notebook.add(self.page2, text="选择题目")

        # 添加 9 个选项卡
        for i in range(1, 10):
            # sudoku_board = generate_sudoku(difficulty=30)
            # puzzle_board = generate_sudoku(30) # pass difficulty level as argument
            sudoku_board = generate_sudoku('easy')
            solved_board = copy.deepcopy(sudoku_board)
            solve_sudoku(solved_board)
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"题目{i}")
            puzzle_label = tk.Label(tab, text="题目:")
            puzzle_label.pack()
            puzzle_text = tk.Text(tab, height=10, width=20)
            puzzle_text.insert(tk.END, "\n".join(" ".join(str(num) for num in row) for row in sudoku_board))
            puzzle_text.pack()
            solution_button = tk.Button(tab, text="查看答案", command=lambda board=solved_board: self.show_solution(board))
            solution_button.pack()

        # 添加开始游戏的按钮
        start_button = tk.Button(self.page1, text="开始游戏", command=self.start_game)
        start_button.pack()

    def start_game(self):
        self.notebook.select(self.page2)

    def show_solution(self, board, row, col):
        solution_window = tk.Toplevel(self.master)
        solution_window.title("题解")
        solution_text = tk.Text(solution_window, height=10, width=20)
        solution_text.insert(tk.END, "\n".join(" ".join(str(num) for num in row) for row in board))
        solution_text.pack()

        removed_num = board[row][col]
        board[row][col] = 0

        # 复制数独以避免修改原始数独
        test_board = copy.deepcopy(board)

        # 检查是否有唯一解
        if solve_sudoku(test_board):
            num_to_remove += 1
        else:
            # 还原清除的数字
            board[row][col] = removed_num

        return board



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
#在main函数中调用GUI
if __name__ == "__main__":
    root = tk.Tk()
    sudoku_gui = SudokuGUI(root)
    root.mainloop()
    sudoku_list = generate_sudoku_parallel()
    # for i, sudoku in enumerate(sudoku_list):
    #     print(f"Sudoku {i + 1} (题目):")
    #     print_sudoku(sudoku[1])  # 使用 puzzle_board
    #     save_sudoku_problem(sudoku[1], f"sudoku_problem_{i + 1}.txt")
        
    #     solved_sudoku = sudoku[0]  # 使用 solved_board
    #     print(f"Sudoku {i + 1} (题解):")
    #     print_sudoku(solved_sudoku)
    #     save_sudoku_solution(solved_sudoku, f"sudoku_solution_{i + 1}.txt")
    #     print()
