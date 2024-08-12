import numpy as np
from sudoku import Sudoku

class SudokuSolver():
    def __init__(self, board):
        # deepcopy
        self.original = [row.copy() for row in board]
        self.board = [row.copy() for row in board]
        self.steps = 0
    
    def valid_assignment(self, row, col, num):
        for i in range(9):
            # horizontal
            if i != col and self.board[row][i] == num:
                return False
            # vertical
            if i != row and self.board[i][col] == num:
                return False
        # square
        for i in range(3):
            for j in range(3):
                shift_hor = row // 3 * 3
                shift_ver = col // 3 * 3
                if (i+shift_hor!=row and j+shift_ver!=col) and self.board[i+shift_hor][j+shift_ver]==num:
                    return False
        return True

    def is_valid(self):
        for row in range(len(self.board)):
            hor = [i+1 for i in range(9)]
            ver = [i+1 for i in range(9)]
            for col in range(len(self.board[row])):
                # horizontal
                if self.board[row][col] in hor:
                    hor.remove(self.board[row][col])
                else:
                    return False
                # vertical
                if self.board[col][row] in ver:
                    ver.remove(self.board[col][row])
                else:
                    return False
            # square
            # 0-(0,0) 1-(0,3) 2-(0,6) 3-(3,0) 4-(3,3) 5-(3,6) 6-(6,0) 7-(6,3) 8-(6,6)
            nums = [i+1 for i in range(9)]
            shift_hor = row // 3 * 3
            shift_ver = row % 3 * 3
            for i in range(3):
                for j in range(3):
                    if self.board[i+shift_hor][j+shift_ver] in nums:
                        nums.remove(self.board[i+shift_hor][j+shift_ver])
                    else:
                        return False
        return True
    
    def print_board(self, original=False):
        board_to_print = self.original if original else self.board
        SudokuSolver.print_structure(board_to_print)

    def print_structure(board):
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("-" * 6 + "+" + "-" * 7 + "+" + "-" * 6)
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("| ", end="")
                if board[i][j] is None:
                    print(f"  ", end="")
                else:
                    print(f"{board[i][j]} ", end="")
            print()
        print()
    
class NaiveBacktrack(SudokuSolver):
    def __init__(self, board):
        super().__init__(board)

    def solve(self):
        if self.backtrack():
            print(f"Found Solution in {self.steps} steps\n")
            self.print_board(original=True)
            self.print_board()
        else:
            print(f"No Solution Found after {self.steps} steps\n")

    def backtrack(self):
        self.steps+=1

        row, col = self.find_unassigned_variable()
        if row is None:
            return True

        for num in range(1, 10):
            if self.valid_assignment(row, col, num):
                self.board[row][col] = num
                if self.backtrack():
                    return True
                self.board[row][col] = None
        return False 

    def find_unassigned_variable(self):
        for row in range(9):
                for col in range(9):
                    if self.board[row][col] is None:
                        return row, col
        return None, None


class SudokuCSP(SudokuSolver):
    def __init__(self):
        pass

def read_board():
    return [[0,0,0,2,6,0,7,0,1],[6,8,0,0,7,0,0,9,0],[1,9,0,0,0,4,5,0,0],
            [8,2,0,1,0,0,0,4,0],[0,0,4,6,0,2,9,0,0],[0,5,0,0,0,3,0,2,8],
            [0,0,9,3,0,0,0,7,4],[0,4,0,0,5,0,0,3,6],[7,0,3,0,1,8,0,0,0]]

def main():
    board = Sudoku(3).difficulty(0.5).board
    solver = NaiveBacktrack(board)
    solver.solve()

if __name__ == "__main__":
    main()