import argparse
from Solver import NaiveBacktrack, ConstraintPropagation
from sudoku import Sudoku

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--Input", help="Optional Input File")
    parser.add_argument("--naive", help="Use Naive Backtracking", action="store_true")
    parser.add_argument("--inference", help="Use Inference when Backtracking", action="store_true")
    parser.add_argument("--mrv", help="Use Minimum Remaining Values", action="store_true")
    parser.add_argument("--lcv", help="Use Least Constraining Values", action="store_true")

    args = parser.parse_args()

    if args.naive:
        solver = NaiveBacktrack(file=args.Input)
    else:
        inference = mrv = lcv = False
        if args.inference:
            inference = True
        if args.mrv:
            mrv = True
        if args.lcv:
            lcv = True
        solver = ConstraintPropagation(file=args.Input, backtrack_inference=inference, minimum_remaining_values=mrv, least_constraining_values=lcv)
    solver.solve()

if __name__ == "__main__":
    main()