import sys
import math
import random
# A game of Tic-Tac-Toe
# Assumes that X goes first.

def drawBoard(board):
    """
    Draws board starting from top left to bottom right with index starting at 0
    """
    print('\n' + '===========================' + '\n')
    print('  1   2   3')
    print('    |   |')
    print('1 ' + board[0] + ' | ' + board[1] + ' | ' + board[2])
    print('    |   |')
    print('------------')
    print('    |   |')
    print('2 ' + board[3] + ' | ' + board[4] + ' | ' + board[5])
    print('    |   |')
    print('-----------')
    print('    |   |')
    print('3 ' + board[6] + ' | ' + board[7] + ' | ' + board[8])
    print('    |   |')

def getPlayerLetter(player):
    """
    Returns 'x' if player is 0. Otherwise, 'o'
    """ 
    return 'x' if player == 0 else 'o'

def getNumPieces(board):
    num_x = board.count('x')
    num_o = board.count('o')
    return (num_x, num_o, 9 - num_x - num_o)

def isBoardFull(board):
    return getNumPieces(board)[2] == 0

def isValidMove(board, current_player, index, undo=False):
    """
    Move is index number on the board.
    Function to check if some move is valid.
    This includes validation for undoing moves too. Cannot undo a move that is blank on the board.
    """
    num_x, num_o, num_blank = getNumPieces(board)
    if undo: # checking if an undo move is valid.
        # just doublechecking we have correct number of pieces.
        if (current_player == 0) and (num_x - 1 != num_o): # x is undoing.
            return False
        elif (current_player == 1) and (num_x != num_o): # o is undoing.
            return False
        elif num_blank == 9:
            return False
        # checking if the move we are trying to undo is not blank. if it is blank, error!
        if board[index] == ' ':
            return False
    else: # checking if a move made on board is valid
        # doublecheck we have correct number of pieces
        if (current_player == 0) and (num_x != num_o):
            print "Invalid 1"
            return False
        elif (current_player == 1) and ((num_x - 1) != num_o):
            print "Invalid 2"
            return False
        elif num_blank == 0:
            print "Invalid 3"
            return False
        # checking if move we are trying to make is already filled
        if board[index] != ' ':
            print "Invalid 4"
            return False
    return True

def makeMove(board, current_player, move):
    """
    Makes a move on the board.
    Assumes move has been validated already.
    """
    board[move] = getPlayerLetter(current_player)
    return board

def undoMove(board, move):
    """
    Tic-Tac-Toe undo is just to remove the piece that was just placed.
    Nothing tricky to consider...I think...
    Assumes move has been validated already.
    """
    board[move] = ' '
    return board

def boardStatus(board, current_player):
    """
    board status for the current_player who just made a move
    """
    WIN, UNDECIDED = 0, 1
    board_size = len(board)
    player_letter = getPlayerLetter(current_player)
    p = int(math.sqrt(board_size)) # number of pieces needed in a row to win
    # brute force checking
    # check horizontally
    for i in range (0, board_size, p):
        num_pieces_in_row = 0
        for j in range(i, i+p):
            if board[j] == player_letter:
                num_pieces_in_row += 1
            else:
                num_pieces_in_row = 0
                break
        if num_pieces_in_row == p:
            return WIN
    # check vertically
    for k in range(0, p):
        num_pieces_in_row = 0
        for l in range(k, board_size, p):
            if board[l] == player_letter:
                num_pieces_in_row += 1
            else:
                num_pieces_in_row = 0
                break
        if num_pieces_in_row == p:
            return WIN
    # check diagonal from top left to bottom right
    for m in range(0, board_size, p+1):
        if board[m] == player_letter:
            num_pieces_in_row += 1
        else:
            num_pieces_in_row = 0
        if num_pieces_in_row == p:
            return WIN
    # check diagonal from top right to bottom left
    for n in range(p-1, board_size, p-1):
        if board[n] == player_letter:
            num_pieces_in_row += 1
        else:
            num_pieces_in_row = 0
        if num_pieces_in_row == p:
            return WIN

    return UNDECIDED

def isWin(board, move, current_player):
    """
    Will check if move will be a winning move for current_player
    Perhaps this might be more optimal than checking game status.
    Will do this later.
    """
    return False
    
def initiateBoard(n):
    board = [' '] * (n * n)
    return board

def getPlayerMove(n):
    number = input("Enter two-digit number for move ") # first number is row, second number is column. Starts from 1
    row = number / 10
    column = number % 10
    index = (row - 1) * n + (column - 1)
    return index


def main():
    args = sys.argv[1:] # just want the arguments after python ttt.py
    assert(len(args)) == 2
    # allowed modes:
    # human vs human
    # human vs computer
    # computer vs human
    first_player = args[0]
    second_player = args[1]
    n = 3
    board = initiateBoard(n)
    game_is_active = True
    need_move = False
    current_player = 0 # toggle player
    if first_player == 'human':
        if second_player == 'computer':
            while game_is_active:
                if current_player == 0: # x's turn
                    drawBoard(board)
                    need_move = not need_move
                    while need_move:
                        move = getPlayerMove(n)
                        if isValidMove(board, current_player, move):
                            makeMove(board, current_player, move)
                            need_move = not need_move
                        else:
                            print "Invalid move. Enter again."
                    if boardStatus(board, current_player) == 0:
                        print "You just won!"
                        game_is_active = not game_is_active
                        break
                    elif isBoardFull(board):
                        print "You have tied!"
                        game_is_active = not game_is_active
                        break
                    current_player = 1 - current_player
                elif current_player == 1:
                    need_move = not need_move
                    while need_move:
                        move = random.randint(0, n*n-1)
                        if isValidMove(board, current_player, move):
                            makeMove(board, current_player, move)
                            need_move = not need_move
                    if boardStatus(board, current_player) == 0:
                        print "You just lost!"
                        game_is_active = not game_is_active
                        break
                    elif isBoardFull(board):
                        print "You have tied!"
                        game_is_active = not game_is_active
                        break
                    current_player = 1 - current_player
                drawBoard(board)


if __name__ == "__main__":
    main()
