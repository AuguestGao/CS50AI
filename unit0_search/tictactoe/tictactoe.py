"""
Tic Tac Toe Player

AG
2021-01-08
"""

import math
import copy

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
    # Count number of 'X' and 'O'
    X_count = sum(row.count(X) for row in board)
    O_count = sum(row.count(O) for row in board)

    # O trun when O_count == X_count, otherwise X turn
    if X_count > O_count:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Init possible actions 
    actions = set()

    # Add (row, cln) to actions when board[i][j] == EMPTY
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i,j))
    # Return actions
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Get all possible actions
    valid_actions  = actions(board)

    # If action is invalid, raise error
    if action not in valid_actions:
        raise Exception("Invalid action")
    else:
        # Unwarp i, j from action
        i, j = action

    # Deepcopy board
    new_board = copy.deepcopy(board)

    # Get who's turn, X or O
    play = player(board)

    # Update new board
    new_board[i][j] = play

    return new_board
    

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Check Horizontal
    for i in board:
        pattern = ''
        for ele in i:
            if ele == None:
                pattern += ' '
            else:
                pattern += ele
        result = check_pattern(pattern)
        
        # return result if not None
        if result:
            return result
            
    
    # Check Vertical
    for i in range(3):
        pattern = ''
        for j in range(3):
            ele = board[j][i]
            if ele == None:
                pattern += ' '
            else:
                pattern += ele
        result = check_pattern(pattern)
        if result:
            return result

    # Check Diagonal 00,11,22
    pattern = ''
    for i in range(3):
        ele = board[i][i]
        if ele == None:
            pattern += ' '
        else:
            pattern += ele
    result = check_pattern(pattern)
    if result:
        return result
    
    pattern = ''
    # Check Diagonal 02,11,20
    for i in range(3):
        ele = board[i][2-i]
        if ele == None:
            pattern += ' '
        else:
            pattern += ele
    result = check_pattern(pattern)
    if result:
        return result
    
    # no winner
    return None
    

def check_pattern(pattern):
    """
    Return winner X, O or None
    Called by winner function
    """
    if pattern == 'XXX':
        return X
    elif pattern == 'OOO':
        return O
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if there is a winner
    if not winner(board):
        # No winner
        # If there is still EMPTY: game in progress
        for row in board:
            if None in row:
                return False
        # No EMPTY spot: game done without a winner
        return True
    # Has a winner
    else:
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    #get the winner
    who_win = winner(board)
    if who_win == X:
        return 1
    elif who_win == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    if player(board) == X:
        _, move = max_value(board)
        return move
    else:
        _, move = min_value(board)
        return move
    

def max_value(board):
    
    # Check if it's a terminal board 
    if terminal(board):
        return (utility(board), None)

    # Init score for max player -inf
    score = float('-inf')
    move = None

    for action in actions(board):
        new_score, _ = min_value(result(board, action))

        # Update if new score is higher
        if score < new_score:
            score = new_score
            move = action
            
            # Highest score possible, return without checking further
            if score == 1:
                return (score, move)
    return (score, move)


def min_value(board):
    # Check if it's a terminal board 
    if terminal(board):
        return (utility(board), None)

    # Init score for min player inf
    score = float('inf')
    move = None
    
    for action in actions(board):
        new_score, _ = max_value(result(board, action))
        
        # Update if new score is lower
        if score > new_score:
            score = new_score
            move = action
            
            # Lowest score possible, return without checking further
            if score == -1:
                return (score, move)
    return (score, move)

