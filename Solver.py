class InvalidBoard(Exception): pass

class SudokuSolver():
    def __init__(self, board):
        # deepcopy
        self.original = [row.copy() for row in board]
        self.board = [row.copy() for row in board]
        if not self.is_valid():
            raise InvalidBoard("Inputed Sudoku board is not valid")
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
    def __init__(self, board):
        super().__init__(board)

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


class SudokuCSP(SudokuSolver):
    def __init__(self, board, backtrack_inference=False, minimum_remaining_values=False, least_constraining_values=False):
        super().__init__(board)

        # store unassigned variables
        self.variables = dict()
        for row in range(9):
            for col in range(9):
                if self.board[row][col] is None:
                    self.variables[(row, col)] = self.Variable(row, col)
                    self.variables[(row, col)].limit_domain(self.board)
        
        self.constraints = dict()
        for var in self.variables.values():
            self.constraints[var] = self.get_constraints(var)

        self.inference = backtrack_inference
        self.mrv = minimum_remaining_values
        self.lcv = least_constraining_values
         

    def solve(self):
        self.ac3()
        if self.backtrack():
            print(f"Found Solution in {self.steps} steps\n")
            # self.print_board(original=True)
            # self.print_board()
        else:
            print(f"No Solution Found after {self.steps} steps\n")
 
    def ac3(self, arcs=None):
        queue = []
        if arcs is None:
            for var in self.variables.values():
                for constraint in self.constraints[var]:
                    if (constraint, var) not in queue:
                        queue.append((var, constraint))
        else:
            queue = arcs
        
        while len(queue)>0:
            (x, y) = queue.pop(0)
            if self.revise(x, y):
                if len(x.domain)==0:
                    return False
                for z in (self.constraints[x] - {y}):
                    queue.append((z, x))
        return True
    
    def get_constraints(self, var):
        constraints = set()
        for i in range(9):
            # horizontal
            if i != var.col and (var.row, i) in self.variables:
                constraints.add(self.variables[(var.row, i)])
            # vertical
            if i != var.row and (i, var.col) in self.variables:
                constraints.add(self.variables[(i, var.col)])
        # square
        for i in range(3):
            for j in range(3):
                shift_hor = var.row // 3 * 3
                shift_ver = var.col // 3 * 3
                if (i+shift_hor!=var.row and j+shift_ver!=var.col) and (i+shift_hor, j+shift_ver) in self.variables:
                    constraints.add(self.variables[(i+shift_hor, j+shift_ver)])
        return constraints

    def revise(self, x, y):
        # Makes x arc consisitent with y, statisfies binary constraints
        revised = False
        copy = x.domain.copy()

        for x_val in copy:
            delete = True
            for y_val in y.domain:
                if x_val != y_val:
                    delete = False
            if delete:
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
                    self.ac3([(y, var) for y in self.constraints[var]])

                if self.backtrack():
                    return True
                
                self.board[var.row][var.col] = None

                if self.inference:
                    self.reset_domain(original_domains)
        return False 
    
    def get_domain(self):
        domain = dict()
        for var in self.variables.values():
            domain[var] = var.domain.copy()
        return domain
    
    def reset_domain(self, domain):
        for var in self.variables.values():
            var.domain = domain[var]
    
    def find_unassigned_variable(self):
        # if mrv choose based on smallest domain and highest degree if tied
        if self.mrv:
            unassigned = [var for var in self.variables.values() if self.board[var.row][var.col] is None]
            unassigned.sort(key = lambda x: len(self.constraints[x]), reverse=True)
            unassigned.sort(key = lambda x: len(x.domain))
            return unassigned[0] if len(unassigned)>0 else None

        for var in self.variables.values():
            if self.board[var.row][var.col] is None:
                return var
        return None

    def order_domain(self, var):
        # if lcv order domain vals by lowest appearance in other constrained variable domains 
        if not self.lcv:
            return var.domain
        
        domain_constraint = {
            val: 0
            for val in var.domain
        }

        for val in var.domain:
            for constraint in self.constraints[var]:
                if self.board[constraint.row][constraint.col] is None:
                    for val2 in constraint.domain:
                        if val==val2:
                            domain_constraint[val] += 1
        return sorted(domain_constraint, key = lambda x: domain_constraint[x])

    class Variable():
        def __init__(self, row, col):
            self.row = row
            self.col = col
            self.value = None
            self.domain = [x for x in range(1, 10)]

        def limit_domain(self, board):
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
            return f"{self.row}, {self.col}"