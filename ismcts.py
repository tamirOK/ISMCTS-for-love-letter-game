import random
from typing import Tuple

from node import Node
from strategy import get_optimal_move, clean_cards, get_guess_card
from collections import defaultdict
from cardclasses import Princess, Guard, Priest, Countess, King, Prince, Card


class ISMCTS:
    def get_move(self):
        raise NotImplementedError()

    def get_move(self, rootstate: 'LoveLetterState', itermax: int, verbose: bool = True)-> Tuple['Card', 'Player', "Card"]:
        """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
            Return the best move from the rootstate.
        """
        rootnode = Node()

        # (King, Countess) or (Prince, Countess)
        if Countess() in rootstate.playerHands[rootstate.playerToMove] and \
                (King() in rootstate.playerHands[rootstate.playerToMove] or
                         Prince() in rootstate.playerHands[rootstate.playerToMove]):
            return Countess(), None, None

        for i in range(itermax):
            node = rootnode

            # Determinize
            state = rootstate.clone_and_randomize(vanilla=True)
            # Select
            assert len(state.playerHands[state.playerToMove]) == 2
            while not state.round_over and not node.get_untried_moves(state.get_moves()):
                victim, guess = None, None
                # node is fully expanded and non-terminal
                available_moves = state.get_moves()

                node = node.ucb_select_child(available_moves)
                state.do_move(node.move, victim=victim, guess=guess)

            # Expand
            untried_moves = node.get_untried_moves(state.get_moves())

            if untried_moves and not state.round_over:  # if we can expand (i.e. state/node is non-terminal)
                # at expansion step algorithm chooses node randomly
                assert len(state.playerHands[state.playerToMove]) == 2
                move = random.choice(untried_moves)

                node = node.add_child(move, state.playerToMove)  # add child and descend tree
                state.do_move(move)

            # Simulate
            while not state.round_over and state.get_moves():  # while state is non-terminal
                move = random.choice(state.get_moves())
                assert len(state.playerHands[state.playerToMove]) == 2
                state.do_move(move)

            # Backpropagate
            while node:  # backpropagate from the expanded node and work back to the root node
                node.update(state)
                node = node.parentNode

        # Output some information about the tree - can be omitted
        if verbose:
            print(rootnode.children_to_string())

        final_move = max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited
        return final_move, None, None


class Smart_ISMCTS:
    def get_move(self, rootstate: 'LoveLetterState', itermax: int, verbose: bool=True) -> Tuple['Card', 'Player', "Card"]:
        """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
            Return the best move from the rootstate.
        """
        rootnode = Node()

        # (King, Countess) or (Prince, Countess)
        if Countess() in rootstate.playerHands[rootstate.playerToMove] and \
            (King() in rootstate.playerHands[rootstate.playerToMove] or
             Prince() in rootstate.playerHands[rootstate.playerToMove]):
            return Countess(), None, None

        for i in range(itermax):
            node = rootnode

            # Determinize
            state = rootstate.clone_and_randomize()
            # Select
            assert len(state.playerHands[state.playerToMove]) == 2
            while not state.round_over and not node.get_untried_moves(state.get_moves()):
                victim, guess = None, None
                # node is fully expanded and non-terminal
                available_moves = state.get_moves()

                node = node.ucb_select_child(available_moves)

                move = node.move
                if move.name == "Guard":
                    victim, guess = get_guess_card(state.playerToMove, state.seen_cards)
                state.do_move(move, victim=victim, guess=guess)

            # Expand
            untried_moves = node.get_untried_moves(state.get_moves())

            if untried_moves and not state.round_over:  # if we can expand (i.e. state/node is non-terminal)
                # at expansion step algorithm chooses node randomly
                assert len(state.playerHands[state.playerToMove]) == 2
                move, victim, guess = get_optimal_move(state.playerToMove, untried_moves, state.used_cards, state.wrong_guesses,
                                                       state.user_ctl.users,
                                                       state.seen_cards, state.playerHands[state.playerToMove], len(state.deck))

                node = node.add_child(move, state.playerToMove)  # add child and descend tree
                state.do_move(move, victim=victim, guess=guess)

            # Simulate
            while not state.round_over and state.get_moves():  # while state is non-terminal
                move, victim, guess = get_optimal_move(state.playerToMove, state.get_moves(), state.used_cards, state.wrong_guesses, state.user_ctl.users,
                                     state.seen_cards, state.playerHands[state.playerToMove], len(state.deck))

                assert len(state.playerHands[state.playerToMove]) == 2
                state.do_move(move, victim=victim, guess=guess)

            # Backpropagate
            while node:  # backpropagate from the expanded node and work back to the root node
                node.update(state)
                node = node.parentNode

        # Output some information about the tree - can be omitted
        if verbose:
            print(rootnode.children_to_string())

        node = max(rootnode.childNodes, key=lambda c: c.visits)
        final_move = max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited
        if final_move.name == "Guard":
            victim, guess = get_guess_card(rootstate.playerToMove, rootstate.seen_cards)
            if guess:
                return Guard(), victim, guess
        elif len(rootnode.childNodes) > 1 and final_move.name == "Baron" and node.wins / node.visits < 0.6 and \
            rootnode.childNodes[0].move.name != "Princess" and rootnode.childNodes[1].move.name != "Princess":
            return rootnode.childNodes[0].move if rootnode.childNodes[0].move.name != "Baron" else rootnode.childNodes[1].move, None, None

        return final_move, None, None