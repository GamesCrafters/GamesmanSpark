import copy

WIDTH = 4
HEIGHT = 4  
WIN_NUMBER = 4

WIN, LOSE, TIE, UNDECIDED, DRAW = 'WIN', 'LOSE', 'TIE', 'UNDECIDED', 'DRAW'

PLAYER_1 = 'X'
PLAYER_2 = 'O'
EMPTY = '-'

""" Game state is saved as an array, in COLUMN-major order. E.g. in a 2x3 board:

    1 2
    3 4
    5 6

    we would store this as [1, 3, 5, 2, 4, 6].
    Benefit of storing in column-major order is due to how connect 4 is played: one
    can only chose a column to drop their piece in, and it must go to the lowest empty space in that column.
"""
# Initializes an empty board
def init_board():
    return [EMPTY] * WIDTH * HEIGHT

# Returns if the board is empty
def isEmpty(position):
    return position.count(EMPTY) == WIDTH * HEIGHT

# Returns list of columns 
def get_columns(position):
    return [position[i:i+HEIGHT] for i in range(0, WIDTH * HEIGHT, HEIGHT)]

# Returns list of rows 
def get_rows(position):
    return [position[i::HEIGHT] for i in range(0, HEIGHT)]

# Calculates turn based on who has more pieces on the board
def turn(position):
    # Default move is PLAYER_1
    if position.count(PLAYER_1) > position.count(PLAYER_2):
        return PLAYER_2
    else:
        return PLAYER_1

# Returns a list of column indices a piece can be dropped into 
def generate_moves(position):
    columns = get_columns(position)
    return [i for i , c in enumerate(columns) if EMPTY in c]

# move is a integer, representing the column number you want to drop a piece into, returns new board
def do_move(position, move):
    column = get_columns(position)[move]
    last_empty = len(column) - column[::-1].index(EMPTY) - 1

    position[(move * HEIGHT) + last_empty] = turn(position)
    return position

# Returns list of next possible board states
def possible_outcomes(position):
    return [do_move(position, move) for move in generate_moves(position)]

# Helper: gets diagonals with negative slope
def get_negative_diagonals(position):
    start = list(set().union(range(HEIGHT), range(0, HEIGHT * WIDTH, HEIGHT)))
    output = []
    for i in start:
        sublist = []
        while (i+1) % HEIGHT and i < HEIGHT * WIDTH:
            sublist.append(position[i])
            i += HEIGHT + 1

        if i < HEIGHT * WIDTH:
            sublist.append(position[i])
        output.append(sublist)
    
    return output

# Helper: gets diagonals with positive slope
def get_positive_diagonals(position):
    start = list(set().union(range(HEIGHT*(WIDTH-1), HEIGHT*WIDTH), range(0, HEIGHT * WIDTH, HEIGHT)))
    output = []
    for i in start:
        sublist = []
        while (i+1) % HEIGHT and i >= 0:
            sublist.append(position[i])
            i -= (HEIGHT - 1)

        if i >= 0:
            sublist.append(position[i])
        output.append(sublist)
    
    return output

# Returns list of all diagonals
def get_diagonals(position):
    return get_negative_diagonals(position) + get_positive_diagonals(position)

def print_board(position):
    for row in get_rows(position):
        print(row)
    print()

# Returns winning player if winner exists in a board
def winner(position):
    win_p1 = PLAYER_1 * WIN_NUMBER
    win_p2 = PLAYER_2 * WIN_NUMBER
    columns = get_columns(position)
    rows = get_rows(position)
    diagonals = get_diagonals(position)
    for c in columns + rows + diagonals:
        c = ''.join(c)
        if win_p1 in c:
            return PLAYER_1
        elif win_p2 in c:
            return PLAYER_2
    return None

# Returns primitive value of state, or undecided
def primitive(position):
    player = turn(position)
    w = winner(position)
    if w is not None:
        if player == w:
            return WIN
        else:
            return LOSE
    else:
        if EMPTY not in position:
            return TIE
        else:
            return UNDECIDED

# Boolean, if board is primitive
def is_primitive(position):
    return primitive(position) != UNDECIDED

# Returns list of boards which could have let to current board state
def undo_move(position):
    last_player = PLAYER_1 if turn(position) == PLAYER_2 else PLAYER_2

    columns = get_columns(position)
    last_move = lambda x : 0 if EMPTY not in x else len(x) - x[::-1].index(EMPTY)
    indices = [last_move(c) for c in columns]

    last_positions = []
    for possibility in zip(list(range(WIDTH)), indices):
        if possibility[1] < HEIGHT:
            i = (possibility[0] * HEIGHT) + possibility[1]
            if position[i] == last_player:
                undo = copy.copy(position)
                undo[i] = EMPTY
                if not is_primitive(undo):
                    last_positions.append(undo)
        

    return last_positions








