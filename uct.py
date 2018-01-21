from collections import defaultdict
from copy import deepcopy
from typing import Tuple, Union

from cardclasses import Countess
from node import Node
from ismcts import ISMCTS
from strategy import get_guess_card


class Determinized_UCT(ISMCTS):

    def get_move_by_policy(self, state, untried_moves, **kwargs):
        kwargs['random'] = False
        return super().get_move_by_policy(state, untried_moves, **kwargs)

    def select(self, state, node, **kwargs):
        kwargs['extra'] = True
        return super().select(state, node, **kwargs)

    def get_move(self, rootstate: 'LoveLetterState', itermax: int, verbose: bool = True, **kwargs) -> Tuple[
        'Card', Union['Player', None], Union["Card", None]]:
        """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
            Return the best move from the rootstate.
        """
        if self.check_countess(rootstate):
            return Countess(), None, None

        moves = rootstate.get_moves()

        if len(moves) == 1 or moves[0] == moves[1]:
            if moves[0].name == "Guard":
                victim, guess = get_guess_card(rootstate.playerToMove, rootstate.seen_cards)
                if guess:
                    return moves[0], victim, guess
            return moves[0], None, None

        trees_number = kwargs.get('trees_number', 40)

        decision_counter = defaultdict(int)

        for j in range(trees_number):
            state_copy = rootstate.clone_and_randomize()
            rootnode = Node()
            for i in range(itermax // trees_number):
                state = deepcopy(state_copy)
                node = rootnode
                # determinize
                node = self.select(state, node)
                node = self.expand(state, node)
                self.simulate(state)
                self.backpropagate(state, node)
            decision_counter[self.select_final_move(rootnode, rootstate)[0]] += 1

        # Output some information about the tree - can be omitted
        print("{} -> {}".format(moves[0], decision_counter[moves[0]]))
        print("{} -> {}".format(moves[1], decision_counter[moves[1]]))

        if decision_counter[moves[0]] >= decision_counter[moves[1]]:
            if moves[0].name == "Guard":
                # if final move is Guard, then guess card
                victim, guess = get_guess_card(rootstate.playerToMove, rootstate.seen_cards)
                if guess:
                    return moves[0], victim, guess
            return moves[0], None, None
        else:
            if moves[1].name == "Guard":
                # if final move is Guard, then guess card
                victim, guess = get_guess_card(rootstate.playerToMove, rootstate.seen_cards)
                if guess:
                    return moves[1], victim, guess
            return moves[1], None, None
