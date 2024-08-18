from copy import deepcopy
import numpy as np

from .board import ChessBoard


class MCTSNode:
    def __init__(self, board: ChessBoard, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.total_eval = 0
        self.mean_eval = 0
        self.untried_moves = board.get_all_legal_moves()  # List of legal moves in the board
    
    
    def is_fully_expanded(self):
        return len(self.untried_moves) == 0
    
    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.mean_eval + c_param*(2* (2*np.log(self.visits)/child.total_eval)**0.5))
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]
    
    def add_child(self):
        move = self.untried_moves.pop()
        new_board = deepcopy(self.board)
        new_board.make_move(*move)

        child_node = MCTSNode(board=new_board, parent=self, move=move)
        # self.untried_moves.remove(move)
        self.children.append(child_node)
        return child_node

def select_node(node):
    while not node.board.check_game_over() and node.is_fully_expanded():
        node = node.best_child()
    return node

def expand_node(node):
    return node.add_child()

def simulate(node, model):
    return model.predict([node.board.ai_input_list])

def backpropagate(node, result):
    while node is not None:
        node.visits += 1
        node.total_eval += result
        node.mean_eval = node.total_eval / node.visits
        node = node.parent
        
def mcts(root, model, n_simulations):
    print("start")
    for _ in range(n_simulations):
        node = select_node(root)
        game_over_check = node.board.check_game_over()
        
        if not game_over_check:
            node = expand_node(node)
            result = simulate(node, model)[0][0]
        elif game_over_check == 1:
            result = 1000000
        elif game_over_check == -1:
            result = -1000000
        else:
            result = 0

        backpropagate(node, result)
    return root.best_child(c_param=0)  # c_param=0 to select the move with the highest mean eval