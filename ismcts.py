import random

from node import Node
from strategy import get_optimal_move, clean_cards, get_guess_card
from rule_based import get_move
from collections import defaultdict
from cardclasses import Princess, Guard, Priest, Countess, King, Prince, Card, Baron


class ISMCTS(object):

    def check_countess(self, rootstate):
        # if hand is (King, Countess) or (Prince, Countess), play the Countess
        return Countess() in rootstate.playerHands[rootstate.playerToMove] and \
                (King() in rootstate.playerHands[rootstate.playerToMove] or
                 Prince() in rootstate.playerHands[rootstate.playerToMove])

    def get_move_by_policy(self, state, untried_moves, **kwargs):
        return get_optimal_move(state.playerToMove, untried_moves, state.used_cards,
                         state.wrong_guesses, state.user_ctl.users,
                         state.seen_cards, state.playerHands[state.playerToMove],
                         len(state.deck), real_players=state.real_players, random=kwargs.get('random', True),
                         playerHands=state.playerHands)

    def select(self, state, node, **kwargs):
        """
        Selection step
        :param state: current state of the game
        :return:
        """
        assert len(state.playerHands[state.playerToMove]) == 2
        while not state.round_over and not node.get_untried_moves(state.get_moves()):
            victim, guess = None, None
            # node is fully expanded and non-terminal
            available_moves = state.get_moves()
            node = node.ucb_select_child(available_moves)
            if node.move.name == "Guard" and kwargs.get('extra', False):
                victim, guess = get_guess_card(state.user_ctl.users, state.playerToMove, state.seen_cards)
            state.do_move(node.move, victim=victim, guess=guess, verbose=kwargs.get('verbose', False))
        return node

    def expand(self, state, node, **kwargs):
        """
        Expansion step
        :param state: current state of the game
        :param node: last node in the game tree
        :return:
        """
        untried_moves = node.get_untried_moves(state.get_moves())

        if untried_moves and not state.round_over:  # if we can expand (i.e. state/node is non-terminal)
            # at expansion step algorithm chooses node randomly
            assert len(state.playerHands[state.playerToMove]) == 2
            move, victim, guess = self.get_move_by_policy(state, untried_moves)
            node = node.add_child(move, state.playerToMove)  # add child and descend tree
            state.do_move(move, victim=victim, guess=guess, verbose=kwargs.get('verbose', False))

        return node

    def simulate(self, state, **kwargs):
        """
        Simulation step
        :param state: current game state
        :return:
        """
        while not state.round_over and state.get_moves():  # while state is non-terminal
            move, victim, guess = self.get_move_by_policy(state, state.get_moves())
            assert len(state.playerHands[state.playerToMove]) == 2
            state.do_move(move, verbose=kwargs.get('verbose', False))

    def backpropagate(self, state, node):
        while node:  # backpropagate from the expanded node and work back to the root node
            node.update(state)
            node = node.parentNode

    def select_final_move(self, rootnode, rootstate):
        final_move = max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited
        return final_move, None, None

    def get_move(self, rootstate, itermax, verbose = True, **kwargs):
        """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
            Return the best move from the rootstate.
        """

        # print(rootstate.playerHands[rootstate.playerToMove])

        assert len(rootstate.playerHands[rootstate.playerToMove]) == 2

        move, victim, guess = get_move(rootstate, ismcts=True)

        if move:
            return move, victim, guess

        rootnode = Node()
        counter = 0
        for i in range(itermax):
            node = rootnode
            # determinize
            state = rootstate.clone_and_randomize(vanilla=kwargs.get('vanilla', True))
            node = self.select(state, node)
            node = self.expand(state, node)
            self.simulate(state)
            self.backpropagate(state, node)

        # Output some information about the tree - can be omitted
        if verbose:
            print(rootnode.children_to_string())

        return self.select_final_move(rootnode, rootstate)


class Smart_ISMCTS(ISMCTS):

    def get_move_by_policy(self, state, untried_moves, **kwargs):
        kwargs['random'] = False
        return super(Smart_ISMCTS, self).get_move_by_policy(state, untried_moves, **kwargs)

    def select(self, state, node, **kwargs):
        kwargs['extra'] = True
        return super(Smart_ISMCTS, self).select(state, node, **kwargs)

    def get_move(self, rootstate, itermax, verbose = False, **kwargs):
        return super(Smart_ISMCTS, self).get_move(rootstate, itermax, verbose=verbose, vanilla=False)

    def select_final_move(self, rootnode, rootstate):
        node = max(rootnode.childNodes, key=lambda c: c.visits)
        final_move = max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited

        opponent, guess = None, None
        # play against human player if we can
        if rootstate.real_players and not rootstate.real_players[0].lost and not rootstate.real_players[0].defence:
            opponent = rootstate.real_players[0]

        if final_move.name == "Guard":
            # if final move is Guard, then guess card
            opponent, guess = get_guess_card(rootstate.user_ctl.users, rootstate.playerToMove, rootstate.seen_cards)
        # control treshold for playing the Baron
        elif len(rootnode.childNodes) > 1 and final_move.name == "Baron" and node.wins / node.visits < 0.6 and \
                rootnode.childNodes[0].move.name != "Princess" and rootnode.childNodes[1].move.name != "Princess":
            if rootnode.childNodes[0].move.name != "Baron":
                return rootnode.childNodes[0].move, opponent, None
            else:
                return rootnode.childNodes[1].move, opponent, None

        return final_move, opponent, None
