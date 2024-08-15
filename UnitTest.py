import unittest
from Solver import SudokuSolver, NaiveBacktrack
from sudoku import Sudoku
import random

N = 10

# |--------------Sudoku Solver--------------|
class TestIsValid(unittest.TestCase):
    def test_solutions(self):
        for _ in range(N):
            solver = SudokuSolver(Sudoku(3).difficulty(0.5).solve().board)
            self.assertEqual(solver.is_valid(), True)

    def test_invalid(self):
        for _ in range(N):
            solution = Sudoku(3).difficulty(0.5).solve().board
            i = random.randint(0, 8)
            j = random.randint(0, 8)
            solution[i][j]+=1
            if(solution[i][j]==10):
                solution[i][j]-=2
            solver = SudokuSolver(solution)
            self.assertEqual(solver.is_valid(), False)

class TestValidConstraints(unittest.TestCase):
    def test_valid(self):
        for _ in range(N):
            i = random.randint(0, 8)
            j = random.randint(0, 8)
            solution = Sudoku(3).difficulty(0.5).solve().board
            solver = SudokuSolver(solution)
            self.assertEqual(solver.valid_assignment(i, j, solution[i][j]), True)

    def test_invalid(self):
        for _ in range(N):
            i = random.randint(0, 8)
            j = random.randint(0, 8)
            solution = Sudoku(3).difficulty(0.5).solve().board
            false = solution[i][j]+1
            if(false==10):
                false-=2
            solver = SudokuSolver(solution)
            self.assertEqual(solver.valid_assignment(i, j, false), False)

# |--------------Naive Backtrack--------------|
class TestNaiveSolver(unittest.TestCase):
    def test_valid(self):
        for _ in range(N):
            sudoku = Sudoku(3).difficulty(random.random())
            solution = NaiveBacktrack(sudoku.board)
            solution.solve()
            self.assertEqual(solution.board, sudoku.solve().board)

    # def test_invalid(self):
    #     for _ in range(N):
    #         i = random.randint(0, 8)
    #         j = random.randint(0, 8)
    #         solution = Sudoku(3).difficulty(0.5).solve().board
    #         false = solution[i][j]+1
    #         if(false==10):
    #             false-=2
    #         solver = SudokuSolver(solution)
    #         self.assertEqual(solver.valid_assignment(i, j, false), False)

if __name__ == '__main__':
    unittest.main()