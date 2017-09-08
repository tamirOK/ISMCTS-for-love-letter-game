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
import random, sys
from copy import deepcopy


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


class Card:
    """ A playing card, with rank and suit.
        rank must be an integer between 1 and 8 inclusive 
    """

    def __init__(self, rank):
        if not 1 <= rank <= 8:
            raise Exception("Invalid card")
        self.rank = rank

    def __repr__(self):
        return self.rank

    def __eq__(self, other):
        return self.rank == other.rank

    def __ne__(self, other):
        return self.rank != other.rank


class LoveLetterState(GameState):
    """
     A state of the game love letter.
    """

    def __init__(self, n):
        """ Initialise the game state. n is the number of players (from 2 to 4).
        """
        self.numberOfPlayers = n
        self.playerToMove = 1
        self.cardnumber = 15
        self.playerHands = {p: [] for p in xrange(1, self.numberOfPlayers + 1)}
        self.knowledge = {p: [] for p in xrange(1, self.numberOfPlayers + 1)}
        self.knockedOut = {p: False for p in xrange(1, self.numberOfPlayers + 1)}
        self.discards = []  # Stores the cards that have been played already in this round
        self.currentTrick = []
        self.tricksTaken = {}  # Number of tricks taken by each player this round
        self.round = 1
        self.deal()

    def clone(self):
        """ Create a deep clone of this game state.
        """
        st = LoveLetterState(self.numberOfPlayers)
        st.playerToMove = self.playerToMove
        st.round = self.round
        st.playerHands = deepcopy(self.playerHands)
        st.discards = deepcopy(self.discards)
        st.currentTrick = deepcopy(self.currentTrick)
        st.tricksTaken = deepcopy(self.tricksTaken)
        return st

    def clone_and_randomize(self, observer):
        """ Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
        """
        st = self.clone()

        # The observer can see his own hand and the cards in the current trick, and can remember the cards played in previous tricks
        seenCards = st.playerHands[observer] + st.discards + [card for (player, card) in st.currentTrick]
        # The observer can't see the rest of the deck
        st.deck = [card for card in st.get_card_deck() if card not in seenCards]

        # Deal the unseen cards to the other players
        random.shuffle(st.deck)
        for p in xrange(1, st.numberOfPlayers + 1):
            if p != observer:
                st.playerHands[p] = self.deck.pop(0)

        return st

    def get_moves(self):
        return self.playerHands[self.playerToMove]

    def get_card_deck(self):
        """ Construct a standard deck of 16 cards.
        """
        deck = []
        for rank in xrange(2, 8 + 1):
            card_number = 1
            if rank == 1:
                card_number = 5
            elif rank <= 5:
                card_number = 2
            deck.extend([Card(rank) for _ in range(card_number)])
        return deck

    def deal(self):
        """ Reset the game state for the beginning of a new round, and deal the cards.
        """
        self.discards = []
        self.currentTrick = []
        self.tricksTaken = {p: 0 for p in xrange(1, self.numberOfPlayers + 1)}

        # Construct a deck, shuffle it, and deal it to the players
        self.deck = self.get_card_deck()
        random.shuffle(self.deck)
        for p in xrange(1, self.numberOfPlayers + 1):
            self.playerHands[p].append(self.deck.pop())

    def get_next_player(self, p):
        """ Return the player to the left of the specified player, skipping players who have been knocked out
        """
        next = (p % self.numberOfPlayers) + 1
        # Skip any knocked-out players
        while next != p and self.knockedOut[next]:
            next = (next % self.numberOfPlayers) + 1
        return next

    def do_move(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """

        if move == 1:
            # стражница

            # choose player to guess
            player_to_guess = None
            while not player_to_guess or player_to_guess == self.playerToMove:
                player_to_guess = random.randint(1, self.numberOfPlayers)

            # choose card to guess
            seenCards = self.playerHands[self.playerHands] + self.discards + [card for (player, card) in self.currentTrick]

            for player, cards in self.knowledge:
                seenCards += cards

            counter = defaultdict(0)
            max_frequency, max_frequency_cards = 0, set()
            for card in self.get_card_deck():
                if card not in seenCards:
                    counter[card] += 1
                max_frequency = max(max_frequency, counter[card])

            for card in self.get_card_deck():
                if counter[card] == max_frequency:
                    max_frequency_cards.add(card)

            chosen_card = random.choice(max_frequency_cards)

            # correct guess
            if chosen_card in self.playerHands[player_to_guess]:
                self.
                self.numberOfPlayers -= 1

        # Store the played card in the current trick
        self.currentTrick.append((self.playerToMove, move))

        # Remove the card from the player's hand
        self.playerHands[self.playerToMove].remove(move)

        # Find the next player
        self.playerToMove = self.get_next_player(self.playerToMove)

        # If the next player has already played in this trick, then the trick is over
        if any(True for (player, card) in self.currentTrick if player == self.playerToMove):
            # Sort the plays in the trick: those that followed suit (in ascending rank order), then any trump plays (in ascending rank order)
            (leader, leadCard) = self.currentTrick[0]
            suitedPlays = [(player, card.rank) for (player, card) in self.currentTrick if card.suit == leadCard.suit]
            trumpPlays = [(player, card.rank) for (player, card) in self.currentTrick if card.suit == self.trumpSuit]
            sortedPlays = sorted(suitedPlays, key=lambda (player, rank): rank) + sorted(trumpPlays,
                                                                                        key=lambda (player, rank): rank)
            # The winning play is the last element in sortedPlays
            trickWinner = sortedPlays[-1][0]

            # Update the game state
            self.tricksTaken[trickWinner] += 1
            self.discards += [card for (player, card) in self.currentTrick]
            self.currentTrick = []
            self.playerToMove = trickWinner

            # If the next player's hand is empty, this round is over
            if not self.playerHands[self.playerToMove]:
                self.tricksInRound -= 1
                self.knockedOut = {p: (self.knockedOut[p] or self.tricksTaken[p] == 0) for p in
                                   xrange(1, self.numberOfPlayers + 1)}
                # If all but one players are now knocked out, the game is over
                if len([x for x in self.knockedOut.itervalues() if not x]) <= 1:
                    self.tricksInRound = 0

                self.deal()


    def get_result(self, player):
        """ Get the game result from the viewpoint of player. 
        """
        return 0 if (self.knockedOut[player]) else 1

    def take_card_from_deck(self):
        self.playerHands[self.playerToMove].append(self.deck.pop())

    def __repr__(self):
        """ Return a human-readable representation of the state
        """
        result = "Round %i" % self.round
        result += " | P%i: " % self.playerToMove
        result += ",".join(str(card) for card in self.playerHands[self.playerToMove])
        result += " | Tricks: %i" % self.tricksTaken[self.playerToMove]
        result += " | Trick: ["
        result += ",".join(("%i:%s" % (player, card)) for (player, card) in self.currentTrick)
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

    def GetUntriedMoves(self, legalMoves):
        """ Return the elements of legalMoves for which this node does not have children.
        """

        # Find all moves for which this node *does* have children
        triedMoves = [child.move for child in self.childNodes]

        # Return all moves that are legal but have not been tried yet
        return [move for move in legalMoves if move not in triedMoves]

    def UCBSelectChild(self, legalMoves, exploration=0.7):
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
        state = rootstate.clone_and_randomize(rootstate.playerToMove)

        # Select
        state.take_card_from_deck()
        while not node.GetUntriedMoves(state.get_moves()):  # node is fully expanded and non-terminal
            node = node.UCBSelectChild(state.get_moves())
            state.do_move(node.move)

        # Expand
        untriedMoves = node.GetUntriedMoves(state.get_moves())
        if untriedMoves:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(untriedMoves)
            player = state.playerToMove
            state.do_move(m)
            node = node.add_child(m, player)  # add child and descend tree

        # Simulate
        while state.get_moves():  # while state is non-terminal
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

    while True:
        print str(state)
        # Use different numbers of iterations (simulations, tree nodes) for different players
        if state.playerToMove == 1:
            m = ISMCTS(rootstate=state, itermax=1000, verbose=False)
        else:
            m = ISMCTS(rootstate=state, itermax=100, verbose=False)
        print "Best Move: " + str(m) + "\n"
        state.do_move(m)

    someoneWon = False
    for p in xrange(1, state.numberOfPlayers + 1):
        if state.get_result(p) > 0:
            print "Player " + str(p) + " wins!"
            someoneWon = True
    if not someoneWon:
        print "Nobody wins!"


if __name__ == "__main__":
    PlayGame()