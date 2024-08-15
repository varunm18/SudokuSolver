from Solver import NaiveBacktrack, SudokuCSP
from sudoku import Sudoku

def read_board():
    return [[5, None, None,  None, None, 5,  None, 8, None],
    [None, None, None,  6,    None, 1,  None, 4, 3],
    [None, None, None,  None, None, None, None, None, None],
    [None, 1,    None,  5,    None, None, None, None, None],
    [None, None, None,  1,    None, 6,  None, None, None],
    [3,    None, None,  None, None, None, None, None, 5],
    [5,    3,    None,  None, None, None, None, 6, 1],
    [None, None, None,  None, None, None, None, None, 4],
    [None, None, None,  None, None, None, None, None, None]]

def main():
    # board = Sudoku(3).difficulty(0.99).board
    # solver = NaiveBacktrack(board)
    # solver.solve()

    board = Sudoku(3).difficulty(0.6).board
    solver = SudokuCSP(board, backtrack_inference=True, minimum_remaining_values=True, least_constraining_values=True)
    solver.solve()
    solver = SudokuCSP(board, backtrack_inference=True, minimum_remaining_values=True)
    solver.solve()
    solver = SudokuCSP(board, backtrack_inference=False, minimum_remaining_values=False, least_constraining_values=True)
    solver.solve()
    solver = SudokuCSP(board, backtrack_inference=True)
    solver.solve()
    solver = SudokuCSP(board, backtrack_inference=False)
    solver.solve()
    solver = NaiveBacktrack(board)
    solver.solve()

if __name__ == "__main__":
    main()