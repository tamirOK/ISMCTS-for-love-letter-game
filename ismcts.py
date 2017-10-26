import random

from .game import Node
from strategy import get_optimal_move


def ISMCTS(rootstate, itermax, verbose=False):
    """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
    """

    rootnode = Node()

    for i in range(itermax):
        node = rootnode

        # Determinize
        state = rootstate.clone_and_randomize()
        # Select
        while not state.round_over and not node.get_untried_moves(state.get_moves()):
            # node is fully expanded and non-terminal
            available_moves = state.get_moves()

            node = node.ucb_select_child(available_moves)

            move = state.check_move(node.move, available_moves)
            # state.clean_wrong_guesses(move)
            state.do_move(move)

        # Expand
        untriedMoves = node.get_untried_moves(state.get_moves())

        if untriedMoves and not state.round_over:  # if we can expand (i.e. state/node is non-terminal)
            # at expansion step algorithm chooses node randomly
            m = random.choice(untriedMoves)
            # state.clean_wrong_guesses()
            state.do_move(m)
            node = node.add_child(m, state.playerToMove)  # add child and descend tree

        # Simulate
        while not state.round_over and state.get_moves():  # while state is non-terminal
            # TODO: smart move selection
            m = get_optimal_move(state.get_moves(), state.used_cards, state.wrong_guesses, state.user_ctl.users,
                                 state.seen_cards[state.playerToMove])
            # m = state.check_move(m, state.get_moves())

            # state.clean_wrong_guesses(m)
            state.do_move(m)


        # Backpropagate
        while node:  # backpropagate from the expanded node and work back to the root node
            node.update(state)
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if verbose:
        print(rootnode.tree_to_string(0))
    else:
        print(rootnode.children_to_string())

    final_move = max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited
    if final_move.name == "Princess":
        final_move = rootnode.childNodes[0].move if rootnode.childNodes[0].move != 'Princess' else rootnode.childNodes[1]
    return final_move