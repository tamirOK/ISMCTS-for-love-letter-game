# -*- coding: utf-8 -*-
from collections import defaultdict
from math import *
from cardclasses import *
import random
from copy import deepcopy
from operator import itemgetter


card_dict = {
    'princess': Princess(),
    'countess': Countess(),
    'king': King(),
    'priest': Priest(),
    'maid': Maid(),
    'baron': Baron(),
    'guard': Guard()
}


class User:
    def __init__(self, uid, lost=False):
        self.lost = lost
        self.won_round = False
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

        self.users = [User(uid) for uid in range(1, number_of_players + 1)]
        self.current_player_index = 0

    def add(self, user):
        self.users.append(user)

    def shuffle(self):
        random.shuffle(self.users)

    def next_player(self):
        """
        :return: index of next player to make move 
        """
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
                victims.append(user)
        return victims

    def get_active_user(self, state):
        return self.users[state.playerToMove]

    def clone(self):
        """
        clones current user ctl
        :return: deep clone
        """
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


class LoveLetterState:
    """
     A state of the game love letter.
    """

    def __init__(self, n):
        """ Initialise the game state which are constant during the game. 
            n is the number of players (from 2 to 4).
        """
        self.numberOfPlayers = n
        self.used_cards = []  # Stores the cards that have been played already in this round
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
        # TODO: FIX out card
        st.out_card = deepcopy(self.out_card)
        st.round_over = self.round_over
        st.game_over = self.game_over
        st.deck = st.get_card_deck()
        st.deck.remove(st.out_card)

        counter = 0
        # TODO: Correct this place
        for card in st.used_cards:
            st.deck.remove(card)

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
        # remove current player's cards from deck
        for card in self.playerHands[self.user_ctl.users[self.playerToMove]]:
            st.deck.remove(card)
        # assign random cards for other users
        for user in st.user_ctl.users:
            if user != current_user and not user.lost:
                user.take_card(st)
        return st

    def get_moves(self):
        """
        :return: list of available moves for current user 
        """
        available_moves = self.playerHands[self.user_ctl.users[self.playerToMove]]

        # countess and king or countess and prince are in hand, return move with countess card
        if Countess() in available_moves and (King() in available_moves or Prince() in available_moves):
            return [Countess()]

        return available_moves


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
        """
        :param first_player: player(instance of User class) who starts current round. If None, then random player starts round 
        :return:  
        """
        self.round += 1
        self.round_over = False

        if not hasattr(self, "user_ctl"):
            self.user_ctl = UserCtl(self.numberOfPlayers)
            self.user_ctl.shuffle()
        else:
            for user in self.user_ctl.users:
                user.defence = user.lost = user.won_round = False

        self.deck = self.get_card_deck()
        random.shuffle(self.deck)
        # remove one card from deck and remember it
        self.out_card = self.deck.pop()
        self.playerToMove = self.user_ctl.next_player()
        self.playerHands = {user: [] for user in self.user_ctl.users}
        #  if there is winner in previous round, then he or she starts the next round
        if first_player:
            # place player on first position in player list
            for index, user in enumerate(self.user_ctl.users):
                if index > 0 and user == first_player:
                    self.user_ctl.users[index], self.user_ctl.users[0] = self.user_ctl.users[0], user
                    break

        self.used_cards = []
        self.currentTrick = []

        for user in self.user_ctl.users:
            user.take_card(self)

        # player who makes move takes second card
        self.user_ctl.users[self.playerToMove].take_card(self)

    def do_move(self, move, **kwargs):
        """
        Function apply moves for current player and change state (itself)
        :param move: move to make
        :param verbose: simple logging of every action
        :param global_game: in case of simulation algorithm plays until round ends.
        in case of global gamel multiple rounds are played.
        :return: 
        """
        global_game = kwargs.get('global_game', False)
        victim = kwargs.get('victim')

        if not 'verbose' in kwargs:
            kwargs['verbose'] = False

        # if AI bot made move with princess, make move with another card
        while move.name == "Princess":
            move = random.choice(self.get_moves())

        current_player = self.user_ctl.users[self.playerToMove]

        # deactivate action of defense from previous move
        if current_player.defence:
            current_player.defence = False

        left_players = [player for player in self.user_ctl.users
                        if not player.defence and current_player != player and not player.lost]
        # TODO: smart opponent selection using knowledge about them

        if not victim:
            victim = random.choice(left_players) if left_players else None
            kwargs['victim'] = victim

        # Remove the card from the player's hand
        self.playerHands[current_player].remove(move)
        assert len(self.playerHands[current_player]) == 1

        self.used_cards.append(move)

        move.activate(self, **kwargs)

        # Store the played card in the current trick
        self.currentTrick.append((current_player, move))

        # If only one player left
        if self.user_ctl.players_left_number() == 1:
            winner = self.user_ctl.get_left_player()
            self.tricksTaken[winner] += 1
            winner.won_round = True

            if self.tricksTaken[winner] == 4:
                self.game_over = True

            self.round_over = True
            if global_game:
                print("\n\nRound #{} won by {}".format(self.round, winner))
                self.start_new_round(first_player=winner)

        # deck is empty, so game is over
        elif len(self.deck) == 0:
            for player in self.user_ctl.users:
                assert len(self.playerHands[player]) <= 1

            def played_card_sum(player):
                result = 0
                for moved_player, card in self.currentTrick:
                    if moved_player == player:
                        result += card.value
                return result

            cards = [(player, self.playerHands[player], played_card_sum(player))
                     for player in self.user_ctl.users
                     if not player.lost]

            cards.sort(key=lambda item: (item[1], item[2]), reverse=True)

            winner = cards[0][0]
            winner.won_round = True
            self.tricksTaken[winner] += 1
            if self.tricksTaken[winner] == 4:
                self.game_over = True

            self.round_over = True
            if global_game:
                print("\n\nRound #{} won by {}".format(self.round, winner))
                self.start_new_round(first_player=winner)
        else:
            # Find the next player
            previous_player = self.playerToMove
            self.playerToMove = self.user_ctl.next_player()

            # check that there are more that one player
            assert previous_player != self.playerToMove
            self.user_ctl.users[self.playerToMove].take_card(self)

    def get_result(self, player):
        """ Get the game result from the viewpoint of player. 
        """
        return 1 if player.won_round else 0

    def take_card_from_deck(self):
        self.playerHands[self.playerToMove].append(self.deck.pop())

    def check_move(self, move, available_moves):

        # do not allow to make move with princess card
        while move == Princess():
            move = random.choice(available_moves)
        return move


    def __repr__(self):
        """ Return a human-readable representation of the state
        """
        current_player = self.user_ctl.users[self.playerToMove]
        result = "Round %i" % self.round
        result += " | %s: " % current_player
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
            length of legalMoves always be less that or equal to 2
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

    def tree_to_string(self, indent):
        """ Represent the tree as a string, for debugging purposes.
        """
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.tree_to_string(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def children_to_string(self):
        print("Showing statistic:")
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
        while not state.round_over and not node.get_untried_moves(state.get_moves()):
            # node is fully expanded and non-terminal
            available_moves = state.get_moves()

            node = node.ucb_select_child(available_moves)
            move = state.check_move(node.move, available_moves)
            state.do_move(move)

        # Expand
        untriedMoves = node.get_untried_moves(state.get_moves())

        if untriedMoves and not state.round_over:  # if we can expand (i.e. state/node is non-terminal)
            # at expansion step algorithm chooses node randomly
            m = random.choice(untriedMoves)
            player = state.user_ctl.users[state.playerToMove]
            state.do_move(m)
            node = node.add_child(m, player)  # add child and descend tree

        # Simulate
        while not state.round_over and state.get_moves():  # while state is non-terminal
            # TODO: smart move selection
            m = random.choice(state.get_moves())
            m = state.check_move(m, state.get_moves())

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

    return max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited


def get_single_player_move(state):
    """
    User selects card and victim.
    :param state:
    :return: Move that user selected, victim that user selected, and card to guess (for Guard only)
    """
    card = None

    print("\nNow is your turn, {}. Choose card to move:".format(state.user_ctl.users[state.playerToMove]))
    print("[", " ".join(str(card) for card in state.get_moves()), "]")

    # deactivate defense from previous move
    state.user_ctl.users[state.playerToMove].defence = False

    move_index = int(input())
    move = state.get_moves()[move_index]

    # simple case when player does not need to select victim
    if move == Countess():
        return move, None, card

    # if maid is selected, activate it on player (Rationality assumption)
    if move == Maid():
        return move, state.user_ctl.users[state.playerToMove], card

    print("Now select victim")
    left_players = [player for player in state.user_ctl.users
                    if not player.defence and not player.lost]
    print(left_players)
    victim_index = int(input())

    if move == Guard():
        print("Select card to guess:")
        selected_card = str(input())
        print(type(selected_card))
        card = card_dict[selected_card]

    return move, left_players[victim_index], card


def play_game():
    """ 
    Play a sample game between 4 ISMCTS players.
    """
    state = LoveLetterState(4)
    state.start_new_round()
    real_player = None
    # take card from deck
    print("You are {}".format(real_player))
    while not state.game_over:
        victim, victim_card = None, None

        if state.user_ctl.users[state.playerToMove] == real_player:
            move, victim, victim_card = get_single_player_move(state)
            print("You play with {}".format(move))
        else:
            print("\n", state)
            move = ISMCTS(rootstate=state, itermax=100, verbose=False)
            # print "Best Move: " + str(m) + "\n"
        state.do_move(move, verbose=True, global_game=True, victim=victim, victim_card=victim_card)

    for player in state.user_ctl.users:
        if state.tricksTaken[player] == 4:
            print("Player " + str(player) + " wins!")


if __name__ == "__main__":
    play_game()