from sudoku import Sudoku

class InvalidBoard(Exception): pass

class SudokuSolver():
    def __init__(self, file=None):
        # deepcopy
        if file is None:
            self.board = Sudoku(3).difficulty(0.5).board
        else:
            self.board = self.read_board(file)
        self.original = [row.copy() for row in self.board]

        if not self.is_valid():
            raise InvalidBoard("Inputed Sudoku board is not valid")
        
        self.steps = 0

    def read_board(self, file):
        board = []
        with open(file, 'r') as f:
            for row in f:
                board.append([])
                for num in row.strip():
                    if int(num)==0:
                        board[-1].append(None)
                    else:
                        board[-1].append(int(num))
        return board
    
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
        # check if initial board is valid
        for row in range(len(self.board)):
            hor = [i+1 for i in range(9)]
            ver = [i+1 for i in range(9)]
            for col in range(len(self.board[row])):
                # horizontal
                if self.board[row][col] in hor:
                    hor.remove(self.board[row][col])
                elif self.board[row][col] is not None:
                    return False
                # vertical
                if self.board[col][row] in ver:
                    ver.remove(self.board[col][row])
                elif self.board[col][row] is not None:
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
                    elif self.board[i+shift_hor][j+shift_ver] is not None:
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
    def __init__(self, file=None):
        super().__init__(file)

    def solve(self):
        if self.backtrack():
            print(f"Found Solution in {self.steps} steps\n")
            # self.print_board(original=True)
            # self.print_board()
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

class ConstraintPropagation(SudokuSolver):
    def __init__(self, file=None, backtrack_inference=False, minimum_remaining_values=False, least_constraining_values=False):
        super().__init__(file)

        # store unassigned variables
        self.variables = dict()
        for row in range(9):
            for col in range(9):
                self.variables[(row, col)] = self.Variable(row, col)
                self.variables[(row, col)].limit_domain(self.board)
        
        for var in self.variables.values():
            var.constraints = self.get_constraints(var)

        self.inference = backtrack_inference
        self.mrv = minimum_remaining_values
        self.lcv = least_constraining_values
    
    def get_constraints(self, var):
        constraints = set()
        for i in range(9):
            # horizontal
            if i != var.col:
                constraints.add(self.variables[(var.row, i)])
            # vertical
            if i != var.row:
                constraints.add(self.variables[(i, var.col)])
        # square
        for i in range(3):
            for j in range(3):
                shift_hor = var.row // 3 * 3
                shift_ver = var.col // 3 * 3
                if (i+shift_hor!=var.row and j+shift_ver!=var.col):
                    constraints.add(self.variables[(i+shift_hor, j+shift_ver)])
        return constraints

    def solve(self):
        if self.ac3():

            backtrack = False
            for (row, col) in self.variables:
                if len(self.variables[(row, col)].domain)==1:
                    self.board[row][col] = self.variables[(row, col)].domain[0]
                else:
                    backtrack = True

            # not backtrack -> solution already found 
            if not backtrack or self.backtrack():
                print(f"Found Solution in {self.steps} steps\n")
                self.print_board(original=True)
                self.print_board()
            else:
                print(f"No Solution Found after {self.steps} steps\n")
 
    def ac3(self, arcs=None):
        if arcs is None:
            arcs = []
            for var in self.variables.values():
                for constraint in var.constraints:
                    arcs.append((var, constraint))
        
        while len(arcs)>0:
            (x, y) = arcs.pop(0)
            if self.revise(x, y):
                if len(x.domain)==0:
                    return False
                for z in (x.constraints - {y}):
                    arcs.append((z, x))
        return True
    
    def revise(self, x, y):
        # Makes x arc consisitent with y, statisfies binary constraints
        revised = False
        copy = x.domain.copy()

        for x_val in copy:
            if not any([x_val!=y_val for y_val in y.domain]):
                x.domain.remove(x_val)
                revised = True
        
        return revised

    def backtrack(self):
        self.steps+=1

        var = self.find_unassigned_variable()
        if var is None:
            return True
        
        if self.inference:
            original_domains = self.get_domain()

        ordered_domains = self.order_domain(var)
        for num in ordered_domains:
            if self.valid_assignment(var.row, var.col, num):
                self.board[var.row][var.col] = num
                
                if self.inference:
                    self.ac3([(y, var) for y in var.constraints])

                if self.backtrack():
                    return True
                
                self.board[var.row][var.col] = None

                if self.inference:
                    self.reset_domain(original_domains)
        return False 
    
    def find_unassigned_variable(self):
        # if mrv choose based on smallest domain and highest degree if tied
        if self.mrv:
            unassigned = []
            for var in self.variables.values():
                if len(var.domain) > 1 and self.board[var.row][var.col] is None:
                    unassigned.append(var)
                elif len(var.domain) == 1:
                    self.board[var.row][var.col] = var.domain[0]
            return min(unassigned, key=lambda x: (len(x.domain), -len(x.constraints)), default=None)

        for var in self.variables.values():
            if len(var.domain) > 1:
                return var
        return None
    
    def get_domain(self):
        domain = dict()
        for var in self.variables.values():
            domain[var] = var.domain.copy()
        return domain
    
    def reset_domain(self, domain):
        for var in self.variables.values():
            var.domain = domain[var]

    def order_domain(self, var):
        # if lcv order domain vals by lowest appearance in other constrained variable domains 
        if not self.lcv:
            return var.domain
        
        return sorted(var.domain, key = lambda val: self.count_conflicts(val, var))
    
    def count_conflicts(self, val, var):
        count = 0
        for constraint in var.constraints:
                if len(constraint.domain) > 1:
                    count += sum(1 for val2 in constraint.domain if val == val2)
        return count

    class Variable():
        def __init__(self, row, col):
            self.row = row
            self.col = col
            self.domain = [x for x in range(1, 10)]
            self.constraints = None

        def limit_domain(self, board):
            if board[self.row][self.col] is not None:
                self.domain = [board[self.row][self.col]]
                return
            
            for i in range(9):
                # horizontal
                if i != self.col and board[self.row][i] in self.domain:
                    self.domain.remove(board[self.row][i])
                # vertical
                if i != self.row and board[i][self.col] in self.domain:
                    self.domain.remove(board[i][self.col])
            # square
            for i in range(3):
                for j in range(3):
                    shift_hor = self.row // 3 * 3
                    shift_ver = self.col // 3 * 3
                    if (i+shift_hor!=self.row and j+shift_ver!=self.col) and board[i+shift_hor][j+shift_ver] in self.domain:
                        self.domain.remove(board[i+shift_hor][j+shift_ver])
        
        def __repr__(self):
            return f"({self.row}, {self.col})"