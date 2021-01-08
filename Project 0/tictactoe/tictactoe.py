"""
Tic Tac Toe Player
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
    # No more possible moves to be made if there is a winner
    if winner(board) is not None:
        return None

    # If there is a no winner
    xCount = 0
    oCount = 0

    for row in board:
        for col in row:
            if col == X:
                xCount += 1
            elif col == O:
                oCount += 1
    
    # Check if there is any remaining spaces
    if xCount + oCount == 9:
        return None
    elif xCount == oCount:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possibleActions = set()

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == EMPTY:
                possibleActions.add((row, col))

    if len(possibleActions) != 0:
        return possibleActions
    else:
        return None


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Raise an exception if action is invalid
    if action is None:
        raise Exception("Invalid Action Made")

    # Deep Copy of the board
    resultBoard = copy.deepcopy(board)
    
    # Get current Player
    currentPlayer = player(board)

    # Update the resultBoard with the action
    resultBoard[action[0]][action[1]] = currentPlayer

    return resultBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check if player has won vertically
    def checkVerical(player):
        for col in range(len(board)):
            if board[0][col] == player and board[1][col] == player and board[2][col] == player:
                return True
        return False

    # Check if player has won horizontally
    def checkHorizontal(player):
        for row in range(len(board[0])):
            if board[row][0] == player and board[row][1] == player and board[row][2] == player:
                return True
        return False

    # Check if player has won diagonally
    def checkDiagonally(player):
        diagonal_fromTopLeft = True
        diagonal_fromBottomLeft = True
        
        # Check Top Left to Bottom Right
        for i in range(len(board)):
            # print(f"{i},{i}, topleft")
            if board[i][i] != player:
                diagonal_fromTopLeft = False      

        # Check Bottom Left to Top Right
        for col in reversed(range(len(board))):
            row = (len(board) - 1) - col
            # print(f"{row},{col} bottomLeft")
            if board[row][col] != player:
                diagonal_fromBottomLeft = False

        # If any return true, player has won
        if diagonal_fromBottomLeft or diagonal_fromTopLeft:
            return True
        else:
            return False

    # Check if player has won in any way possible
    def checkPlayer(player):
        if checkHorizontal(player) or checkVerical(player) or checkDiagonally(player):
            return True
        else:
            return False
        
    if checkPlayer(X):
        return X
    elif checkPlayer(O):
        return O
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # If there is a winner
    if winner(board) is not None:
        return True
    
    # If there is a no winner
    xCount = 0
    oCount = 0

    for row in board:
        for col in row:
            if col == X:
                xCount += 1
            elif col == O:
                oCount += 1
    
    # Check if there is any remaining spaces
    if xCount + oCount == 9:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winningPlayer = winner(board)

    if winningPlayer == X:
        return 1
    elif winningPlayer == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # ALPHA - best already explored option along path to the root for maximizer
    # BETA - best already explored option along path to the root for minimizer

    def MAX_VALUE(board, alpha, beta):
        if terminal(board):
            return utility(board)

        score = -999
        for action in actions(board):
            score = max(score, MIN_VALUE(result(board, action), alpha, beta))
            alpha = max(alpha, score)

            # if the best option for maximizer is > best option for beta
            # no need to look at other actions
            if alpha > beta:
                break
        
        return score

    # If AI is O, the Ai will want to generate the lowest maximum score
    def MIN_VALUE(board, alpha, beta):
        if terminal(board):
            return utility(board)

        score = 999 
        for action in actions(board):
            score = min(score, MAX_VALUE(result(board, action), alpha, beta))
            beta = min(beta, score)

            # if the best option for minimizer is < best option for alpha
            # no need to look at other actions
            if beta < alpha:
                break
        
        return score
    
    # Get the current Plyer
    currentPlayer = player(board)

    # Create a List of Nodes to check for the best option
    nodeList = []
    if currentPlayer == X:
        # Add possible actions to the current board into the nodeList
        for action in actions(board):
            nodeList.append(Node(board, action, MIN_VALUE(result(board, action), -999, 999)))

        bestNode = nodeList[0]
        # Check and Returns Node with the best score
        for node in nodeList:
            if node.score > bestNode.score:
                bestNode = node
        return bestNode.action   
    else:
        # Add possible actions to the current board into the nodeList
        for action in actions(board):
            nodeList.append(Node(board, action, MAX_VALUE(result(board, action), -999, 999)))
        
        bestNode = nodeList[0]
        # Check and Returns Node with the best score
        for node in nodeList:
            if node.score < bestNode.score:
                bestNode = node
        return bestNode.action


class Node():
    def __init__(self, state, action, score):
        self.state = state
        self.action = action
        self.score = score