"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
from random import randint

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    NEXT_PLAYER = X

    all_values = [x for y in board for x in y]
    
    if all_values.count(X) > all_values.count(O):
        NEXT_PLAYER = O
    
    return NEXT_PLAYER


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i, row in enumerate(board):
        for j, value in enumerate(row):
            if value is EMPTY:
                actions.add((i,j))
    
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = deepcopy(board)
    
    if new_board[action[0]][action[1]] is not EMPTY:
        raise Exception("Not a valid move")
    new_board[action[0]][action[1]] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    for i in board:
        if len(set(i)) == 1:
            return i[0]
        
    for j in [[board[0][x],board[1][x],board[2][x]] for x in range(3)]:
        if len(set(j)) == 1:
            return j[0]
    
    DIAGONAL_ONE = (0,1,2)
    DIAGONAL_TWO = (2,1,0)

    for diagonal in [DIAGONAL_ONE,DIAGONAL_TWO]:
        dig = [board[diagonal[0]][0],board[diagonal[1]][1], board[diagonal[2]][2]]

        if len(set(dig)) == 1:
            return dig[0]
    
    return None



def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    all_values = [x for y in board for x in y]

    result = winner(board)

    if result is EMPTY and all_values.count(EMPTY) > 0:
        return False
    else:
        return True

    


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    result = winner(board)
    
    if result == X:
        return 1
    elif result == O:
        return -1
    elif result is EMPTY:
        return 0

def actual_player_utility(old_board):
    result = player(old_board)
    if result == X:
        return 1
    elif result == O:
        return -1

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    if terminal(board):
        return None
    
    def find_move(board, x_player):

        if x_player:
            best = (None, float("-inf"))
        else:
            best = (None,float("inf"))

        if terminal(board):
            return (None, utility(board))
        for move in actions(board):
            new_board = result(board,move)
            tup = find_move(new_board, player(new_board) == X)
            tup = (move,tup[1])
            if x_player:
                if tup[1] > best[1]:
                    best = tup
            else:
                if tup[1] < best[1]:
                    best = tup

        return best

    move,_ = find_move(board, player(board) == X)
    return(move)
    



     

