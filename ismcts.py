# -*- coding: utf-8 -*-
# This is a very simple Python 2.7 implementation of the Information Set Monte Carlo Tree Search algorithm.
# The function ISMCTS(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a
# state.GetRandomMove() or state.DoRandomRollout() function.
#
# An example GameState classes for Knockout Whist is included to give some idea of how you
# can write your own GameState to use ISMCTS in your hidden information game.
#
# Written by Peter Cowling, Edward Powley, Daniel Whitehouse (University of York, UK) September 2012 - August 2013.
#
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
#
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai
# Also read the article accompanying this code at ***URL HERE***
from collections import defaultdict
from math import *
from cardclasses import *
import random, sys
from copy import deepcopy
from operator import itemgetter


class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement ISMCTS in any imperfect information game,
        although they could be enhanced and made quicker, for example by using a 
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1, 2, ..., self.numberOfPlayers.
    """

    def __init__(self):
        self.numberOfPlayers = 2
        self.playerToMove = 1

    def get_next_player(self, p):
        """ Return the player to the left of the specified player
        """
        return (p % self.numberOfPlayers) + 1

    def clone(self):
        """ Create a deep clone of this game state.
        """
        st = GameState()
        st.playerToMove = self.playerToMove
        return st

    def clone_and_randomize(self, observer):
        """ Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
        """
        return self.clone()

    def do_move(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        self.playerToMove = self.get_next_player(self.playerToMove)

    def get_moves(self):
        """ Get all possible moves from this state.
        """
        raise NotImplementedException()

    def get_result(self, player):
        """ Get the game result from the viewpoint of player. 
        """
        raise NotImplementedException()

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass


class User:
    def __init__(self, uid, lost=False):
        self.lost = lost
        self.uid = uid
        self.defence = False

    def take_card(self, state):
        state.playerHands[self].append(state.deck.pop())

    def __eq__(self, other):
        return self.uid == getattr(other, 'uid', None)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.uid)

    def __repr__(self):
        return "User {0}".format(self.uid)


class UserCtl:
    def __init__(self, number_of_players):

        self.users = [User(uid) for uid in xrange(1, number_of_players + 1)]
        self.current_player_index = 0

    def add(self, user):
        self.users.append(user)

    def shuffle(self):
        random.shuffle(self.users)

    def next_player(self):
        while self.users[self.current_player_index].lost:
            self.current_player_index += 1
            if self.current_player_index == len(self.users):
                self.current_player_index = 0

        result = self.current_player_index
        self.current_player_index = (self.current_player_index + 1) % len(self.users)
        return result

    def __contains__(self, user):
        return user in self.users

    def kill(self, user):
        user.lost = True

    def players_left_number(self):
        return len([player for player in self.users if not player.lost])

    def get_victims(self, dealer):
        victims = []
        for user in self.users:
            if not user.defence and user.uid != dealer.uid:
                victims.append(user.name)
        return victims

    def clone(self):
        cloned = UserCtl(len(self.users))
        cloned.users = [User(user.uid, user.lost) for user in self.users]
        cloned.current_player_index = self.current_player_index
        return cloned

    def num_users(self):
        return len(self.users)

    def get_left_player(self):
        for player in self.users:
            if not player.lost:
                return player

        raise AssertionError("Error happened!")


class LoveLetterState(GameState):
    """
     A state of the game love letter.
    """

    def __init__(self, n):
        """ Initialise the game state which are constant during the game. 
            n is the number of players (from 2 to 4).
        """
        self.numberOfPlayers = n
        self.used_cards = []  # Stores the cards that have been played already in this round
        # TODO: Add knowledge of each player about others
        self.tricksTaken = defaultdict(int)  # Number of tricks taken by each player
        self.round = 0
        self.game_over = False

    def clone(self):
        """ Create a deep clone of this game state.
        """
        st = LoveLetterState(self.numberOfPlayers)
        st.playerToMove = self.playerToMove
        st.round = self.round
        st.playerHands = defaultdict(list)
        st.used_cards = deepcopy(self.used_cards)
        st.currentTrick = deepcopy(self.currentTrick)
        st.tricksTaken = deepcopy(self.tricksTaken)
        st.out_card = deepcopy(self.out_card)
        st.game_over = self.game_over
        st.deck = st.get_card_deck()
        st.deck.remove(st.out_card)

        counter = 0
        for card in st.used_cards:
            try:
                st.deck.remove(card)
            except ValueError:
                counter += 1
            if counter > 1:
                raise Exception("Отсутсвует к колоде карты")

        random.shuffle(st.deck)
        st.user_ctl = self.user_ctl.clone()

        return st

    def clone_and_randomize(self):
        """ Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
        """
        st = self.clone()
        current_user = st.user_ctl.users[st.playerToMove]
        assert len(self.playerHands[self.user_ctl.users[self.playerToMove]]) == 2
        # assign same card for current user
        st.playerHands[current_user] = deepcopy(self.playerHands[self.user_ctl.users[self.playerToMove]])
        for card in self.playerHands[self.user_ctl.users[self.playerToMove]]:
            st.deck.remove(card)
        # assign random cards for other users
        for user in st.user_ctl.users:
            if user != current_user and not user.lost:
                user.take_card(st)
        return st

    def get_moves(self):
        return self.playerHands[self.user_ctl.users[self.playerToMove]]

    def get_card_deck(self):
        """ Construct a standard deck of 16 cards.
        """
        return [Princess(),
                Countess(),
                King(),
                Prince(),
                Prince(),
                Maid(),
                Maid(),
                Baron(),
                Baron(),
                Priest(),
                Priest(),
                Guard(),
                Guard(),
                Guard(),
                Guard(),
                Guard()]

    def start_new_round(self, first_player=None):
        """ Reset the game state for the beginning of a new round, and deal the cards.
        """
        self.round += 1
        self.user_ctl = UserCtl(self.numberOfPlayers)
        self.user_ctl.shuffle()

        self.deck = self.get_card_deck()
        random.shuffle(self.deck)
        # remove one card from deck and remember it
        self.out_card = self.deck.pop()

        self.playerToMove = self.user_ctl.next_player()
        self.playerHands = {user: [] for user in self.user_ctl.users}
        #  if there is winner in previous round, then he or she starts the next round
        if first_player:
            for index, user in enumerate(self.user_ctl.users):
                if index > 0 and user == first_player:
                    self.user_ctl.users[index], self.user_ctl.users[0] = self.user_ctl.users[0], user
                    break

        self.used_cards = []
        self.currentTrick = []

        for user in self.user_ctl.users:
            user.take_card(self)

        self.user_ctl.users[self.playerToMove].take_card(self)

    def do_move(self, move, verbose=False):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """

        # choose player to guess
        current_player = self.user_ctl.users[self.playerToMove]

        if current_player.defence:
            current_player.defence = False

        left_players = [player for player in self.user_ctl.users
                        if not player.defence and current_player != player and not player.lost]
        victim = random.choice(left_players) if left_players else None


        # Remove the card from the player's hand

        self.playerHands[current_player].remove(move)
        assert len(self.playerHands[current_player]) == 1
        self.used_cards.append(move)

        move.activate(self, victim, verbose)

        # Store the played card in the current trick
        self.currentTrick.append((current_player, move))

        # If only one player left
        if self.user_ctl.players_left_number() == 1:
            winner = self.user_ctl.get_left_player()
            self.tricksTaken[winner] += 1
            if self.tricksTaken[winner] == 4:
                self.game_over = True
            self.last_winner = winner
            self.start_new_round(first_player=winner)
        # deck is empty, so game is over
        elif len(self.deck) == 0:
            for player in self.user_ctl.users:
                assert len(self.playerHands[player]) <= 1

            cards = [(player, self.playerHands[player])
                    for player in self.user_ctl.users
                     if not player.lost]

            cards.sort(key=itemgetter(1), reverse=True)

            # TODO: handle case when one player has greater sum than the others
            winner = cards[0][0]
            self.tricksTaken[winner] += 1
            if self.tricksTaken[winner] == 4:
                self.game_over = True
            self.last_winner = winner
            self.start_new_round(first_player=winner)
        else:
            # Find the next player
            previous_player = self.playerToMove
            self.playerToMove = self.user_ctl.next_player()

            assert previous_player != self.playerToMove
            self.user_ctl.users[self.playerToMove].take_card(self)

    def get_result(self, player):
        """ Get the game result from the viewpoint of player. 
        """
        return 1 if self.tricksTaken[player] == 4 else 0

    def take_card_from_deck(self):
        self.playerHands[self.playerToMove].append(self.deck.pop())

    def __repr__(self):
        """ Return a human-readable representation of the state
        """
        current_player = self.user_ctl.users[self.playerToMove]
        result = "Round %i" % self.round
        result += " | P%s: " % current_player
        result += ",".join(str(card) for card in self.playerHands[current_player])
        # result += " | Tricks: %i" % self.tricksTaken[self.user_ctl.users[self.playerToMove]]
        result += " | Trick: ["
        result += ",".join(("%s:%s" % (player, card)) for (player, card) in self.currentTrick)
        result += "]"
        return result


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
    """

    def __init__(self, move=None, parent=None, playerJustMoved=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.avails = 1
        self.playerJustMoved = playerJustMoved  # the only part of the state that the Node needs later

    def get_untried_moves(self, legalMoves):
        """ Return the elements of legalMoves for which this node does not have children.
        """

        # Find all moves for which this node *does* have children
        triedMoves = [child.move for child in self.childNodes]

        # Return all moves that are legal but have not been tried yet
        return [move for move in legalMoves if move not in triedMoves]

    def ucb_select_child(self, legalMoves, exploration=0.7):
        """ Use the UCB1 formula to select a child node, filtered by the given list of legal moves.
            exploration is a constant balancing between exploitation and exploration, with default value 0.7 (approximately sqrt(2) / 2)
        """

        # Filter the list of children by the list of legal moves
        legalChildren = [child for child in self.childNodes if child.move in legalMoves]

        # Get the child with the highest UCB score
        s = max(legalChildren,
                key=lambda c: float(c.wins) / float(c.visits) + exploration * sqrt(log(c.avails) / float(c.visits)))

        # Update availability counts -- it is easier to do this now than during backpropagation
        for child in legalChildren:
            child.avails += 1

        # Return the child selected above
        return s

    def add_child(self, m, p):
        """ Add a new child node for the move m.
            Return the added child node
        """
        n = Node(move=m, parent=self, playerJustMoved=p)
        self.childNodes.append(n)
        return n

    def update(self, terminalState):
        """ Update this node - increment the visit count by one, and increase the win count by the result of terminalState for self.playerJustMoved.
        """
        self.visits += 1
        if self.playerJustMoved is not None:
            self.wins += terminalState.get_result(self.playerJustMoved)

    def __repr__(self):
        return "[M:%s W/V/A: %4i/%4i/%4i]" % (self.move, self.wins, self.visits, self.avails)

    def TreeToString(self, indent):
        """ Represent the tree as a string, for debugging purposes.
        """
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def children_to_string(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s


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
        while not node.get_untried_moves(state.get_moves()):  # node is fully expanded and non-terminal
            assert len(state.get_moves()) == 2
            node = node.ucb_select_child(state.get_moves())
            state.do_move(node.move)

        # Expand
        untriedMoves = node.get_untried_moves(state.get_moves())
        assert len(state.get_moves()) == 2
        if untriedMoves:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(untriedMoves)
            player = state.user_ctl.users[state.playerToMove]
            state.do_move(m)
            node = node.add_child(m, player)  # add child and descend tree

        # Simulate
        while not state.game_over and state.get_moves():  # while state is non-terminal
            assert len(state.get_moves()) == 2
            state.do_move(random.choice(state.get_moves()))

        # Backpropagate
        while node:  # backpropagate from the expanded node and work back to the root node
            node.update(state)
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if verbose:
        print rootnode.TreeToString(0)
    else:
        print rootnode.children_to_string()

    return max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited


def PlayGame():
    """ Play a sample game between 4 ISMCTS players.
    """
    state = LoveLetterState(4)
    state.start_new_round()
    # take card from deck

    while not state.game_over:
        print(state)
        # Use different numbers of iterations (simulations, tree nodes) for different players
        move = ISMCTS(rootstate=state, itermax=100, verbose=False)
        # print "Best Move: " + str(m) + "\n"
        state.do_move(move, verbose=True)

        if state.round % 3 == 0:
            for player in state.user_ctl.users:
                print(player, state.tricksTaken[player])
            print("#" * 80)

    for player in state.user_ctl.users:
        if state.tricksTaken[player] == 4:
            print "Player " + str(player) + " wins!"


if __name__ == "__main__":
    PlayGame()