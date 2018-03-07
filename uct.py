from collections import defaultdict
from copy import deepcopy

from ismcts import ISMCTS
from node import Node
from rule_based import get_move
from strategy import get_guess_card


class Determinized_UCT(ISMCTS):

    def get_move_by_policy(self, state, untried_moves, **kwargs):
        kwargs['random'] = False
        return super(Determinized_UCT, self).get_move_by_policy(state, untried_moves, **kwargs)

    def select(self, state, node, **kwargs):
        kwargs['extra'] = True
        return super(Determinized_UCT, self).select(state, node, **kwargs)

    def get_move(self, rootstate, itermax, verbose=True, **kwargs):
        """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
            Return the best move from the rootstate.
        """
        print(rootstate.playerHands[rootstate.playerToMove])
        move, victim, guess = get_move(rootstate, ismcts=True)

        if move:
            return move, victim, guess

        moves = rootstate.get_moves()

        trees_number = kwargs.get('trees_number', 50)

        decision_counter = defaultdict(int)

        for j in range(trees_number):
            state_copy = rootstate.clone_and_randomize()
            rootnode = Node()
            counter = 0
            for i in range(itermax // trees_number):
                state = deepcopy(state_copy)
                node = rootnode
                # determinize
                node = self.select(state, node)
                if counter == 5:
                    print(rootnode.tree_to_string(indent=0))
                node = self.expand(state, node)
                if counter == 5:
                    print(rootnode.tree_to_string(indent=0))
                self.simulate(state)
                if counter == 5:
                    print(rootnode.tree_to_string(indent=0))
                self.backpropagate(state, node)
                if counter == 5:
                    print(rootnode.tree_to_string(indent=0))
                    import pdb
                    pdb.set_trace()
                counter += 1
            decision_counter[self.select_final_move(rootnode, rootstate)[0]] += 1

        # Output some information about the tree - can be omitted
        print("{} -> {}".format(moves[0], decision_counter[moves[0]]))
        print("{} -> {}".format(moves[1], decision_counter[moves[1]]))

        if decision_counter[moves[0]] >= decision_counter[moves[1]]:
            if moves[0].name == "Guard":
                # if final move is Guard, then guess card
                victim, guess = get_guess_card(rootstate.user_ctl.users, rootstate.playerToMove, rootstate.seen_cards)
                if guess:
                    return moves[0], victim, guess
            return moves[0], None, None
        else:
            if moves[1].name == "Guard":
                # if final move is Guard, then guess card
                victim, guess = get_guess_card(rootstate.user_ctl.users, rootstate.playerToMove, rootstate.seen_cards)
                if guess:
                    return moves[1], victim, guess
            return moves[1], None, None
