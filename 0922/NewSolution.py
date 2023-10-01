import random

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

        # 尝试填充数字1到9
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

    # 生成一个有解的数独
    solve_sudoku(board)

    # 随机清除一些数字以生成题目
    for _ in range(random.randint(30, 50)):
        row, col = random.randint(0, N - 1), random.randint(0, N - 1)
        while board[row][col] == 0:
            row, col = random.randint(0, N - 1), random.randint(0, N - 1)
        board[row][col] = 0

    return board

if __name__ == "__main__":
    sudoku = generate_sudoku()
    for row in sudoku:
        print(row)
