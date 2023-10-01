import threading
import random
import copy

# 九宫格数独的大小
N = 9

def is_valid_move(board, row, col, num):
    # 检查行是否有重复
    if num in board[row]:
        return False

    # 检查列是否有重复
    if num in [board[i][col] for i in range(N)]:
        return False

    # 检查3x3宫格是否有重复
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

def generate_sudoku():
    # 创建一个空白数独
    board = [[0] * N for _ in range(N)]

    # 随机填充初始数字
    for _ in range(random.randint(10, 30)):
        row, col, num = random.randint(0, N - 1), random.randint(0, N - 1), random.randint(1, N)
        while not is_valid_move(board, row, col, num) or board[row][col] != 0:
            row, col, num = random.randint(0, N - 1), random.randint(0, N - 1), random.randint(1, N)
        board[row][col] = num

    return board

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

if __name__ == "__main__":
    sudoku_list = generate_sudoku_parallel()
    for i, sudoku in enumerate(sudoku_list):
        print(f"Sudoku {i + 1} (题目):")
        print_sudoku(sudoku)
        save_sudoku_problem(sudoku, f"sudoku_problem_{i + 1}.txt")
        
        # 复制数独以避免修改原始数独
        solved_sudoku = copy.deepcopy(sudoku)
        solve_sudoku(solved_sudoku)  # 解数独
        print(f"Sudoku {i + 1} (题解):")
        print_sudoku(solved_sudoku)
        save_sudoku_solution(solved_sudoku, f"sudoku_solution_{i + 1}.txt")
        print()
